# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class HrBankAdvice(models.Model):
    '''
    Bank Advice for Moroccan Payroll
    '''
    _name = 'hr.bank.advice'
    _description = "Moroccan HR Payroll Bank Advice"
    _order = 'date desc, id desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_date(self):
        return fields.Date.context_today(self)

    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('hr.bank.advice') or _('New')

    # Champs de base
    name = fields.Char(
        string='Référence',
        readonly=True,
        default=_get_default_name,
        tracking=True
    )

    note = fields.Text(
        string='Description',
        default='Veuillez effectuer le virement de salaire depuis le compte mentionné ci-dessus vers les comptes bancaires des employés mentionnés ci-dessous:'
    )

    date = fields.Date(
        string="Date de Conseil",
        default=_get_default_date,
        help='La date de conseil est utilisée pour rechercher les fiches de paie',
        required=True,
        tracking=True
    )

    # Informations bancaires
    bank_id = fields.Many2one(
        'res.bank',
        string='Banque',
        help='Sélectionnez la banque à partir de laquelle le salaire va être payé',
        required=True,
        tracking=True
    )

    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string='Compte Bancaire de l\'Entreprise',
        required=True,
        tracking=True
    )

    check_number = fields.Char(string='Numéros de Chèque')

    # Lot de paie
    batch_id = fields.Many2one(
        'hr.payslip.run',
        string='Lot de Paie',
        domain="[('state', 'in', ['close', 'paid'])]",
        tracking=True
    )

    # Informations de l'entreprise
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('sent', 'Envoyé'),
        ('paid', 'Payé'),
        ('cancel', 'Annulé'),
    ], string='Statut', default='draft', index=True, readonly=True, tracking=True)

    # Lignes de conseil
    line_ids = fields.One2many(
        'hr.bank.advice.line',
        'advice_id',
        string='Détails Salaires Employés',
        states={'draft': [('readonly', False)]},
        readonly=True,
        copy=True
    )

    # Champs calculés
    total_amount = fields.Monetary(
        string='Montant Total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )

    employee_count = fields.Integer(
        string='Nombre d\'Employés',
        compute='_compute_employee_count',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Devise',
        readonly=True
    )

    # Champs additionnels pour le Maroc
    reference_externe = fields.Char(
        string='Référence Externe Banque',
        help='Référence fournie par la banque'
    )

    date_execution = fields.Date(
        string='Date d\'Exécution Prévue',
        help='Date prévue pour l\'exécution des virements'
    )

    mode_paiement = fields.Selection([
        ('virement', 'Virement Bancaire'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces')
    ], string='Mode de Paiement', default='virement')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            return {'domain': {'bank_account_id': [('partner_id', '=', self.company_id.partner_id.id)]}}
        return {'domain': {'bank_account_id': []}}

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'bank_account_id' in fields_list:
            company = self.env.company
            bank_accounts = self.env['res.partner.bank'].search([
                ('partner_id', '=', company.partner_id.id)
            ])
            if bank_accounts:
                res['bank_account_id'] = bank_accounts[0].id
        return res

    # Contraintes
    @api.constrains('date', 'date_execution')
    def _check_dates(self):
        for record in self:
            if record.date_execution and record.date_execution < record.date:
                raise ValidationError(_("La date d'exécution ne peut pas être antérieure à la date de conseil."))

    # Calculs
    @api.depends('line_ids.bysal')
    def _compute_total_amount(self):
        for advice in self:
            advice.total_amount = sum(line.bysal for line in advice.line_ids)

    @api.depends('line_ids')
    def _compute_employee_count(self):
        for advice in self:
            advice.employee_count = len(advice.line_ids)

    # Actions
    def create(self, vals_list):
        for vals in vals_list if isinstance(vals_list, list) else [vals_list]:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.advice') or _('New')
        return super().create(vals_list)

    def compute_advice(self):
        """
        Créer les lignes de conseil bancaire et calculer les montants
        """
        for advice in self:
            # Vérifier les prérequis
            if not advice.bank_account_id:
                raise UserError(_('Veuillez définir un compte bancaire pour l\'entreprise.'))

            # Supprimer les anciennes lignes
            advice.line_ids.unlink()

            # Rechercher les fiches de paie
            domain = [
                ('state', '=', 'done'),
                ('date_from', '<=', advice.date),
                ('date_to', '>=', advice.date)
            ]

            if advice.batch_id:
                domain.append(('payslip_run_id', '=', advice.batch_id.id))

            payslips = self.env['hr.payslip'].search(domain)

            if not payslips:
                raise UserError(_('Aucune fiche de paie trouvée pour la période spécifiée.'))

            # Créer les lignes
            lines_to_create = []
            for slip in payslips:
                # Vérifier le compte bancaire de l'employé
                if not slip.employee_id.bank_account_id:
                    raise UserError(_('Veuillez définir un compte bancaire pour l\'employé %s') % slip.employee_id.name)

                # Chercher le salaire net
                payslip_line = slip.line_ids.filtered(lambda l: l.code == 'NET')
                if not payslip_line:
                    continue

                # Vérifier que le montant est positif
                if payslip_line.total <= 0:
                    continue

                lines_to_create.append({
                    'advice_id': advice.id,
                    'account_number': slip.employee_id.bank_account_id.id,
                    'employee_id': slip.employee_id.id,
                    'payslip_id': slip.id,
                    'bysal': payslip_line.total
                })

                # Lier la fiche de paie au conseil
                slip.write({'advice_id': advice.id})

            if lines_to_create:
                self.env['hr.bank.advice.line'].create(lines_to_create)
            else:
                raise UserError(_('Aucun salaire net positif trouvé pour créer le conseil bancaire.'))

    def action_confirm(self):
        """Confirmer le conseil bancaire"""
        for advice in self:
            if not advice.line_ids:
                raise UserError(_('Veuillez d\'abord calculer le conseil bancaire.'))
            advice.write({'state': 'confirm'})
            advice.message_post(body=_("Le conseil bancaire a été confirmé."))

    def action_send(self):
        """Marquer comme envoyé"""
        self.write({'state': 'sent'})
        self.message_post(body=_("Le conseil bancaire a été envoyé à la banque."))

    def action_paid(self):
        """Marquer comme payé"""
        self.write({'state': 'paid'})
        self.message_post(body=_("Les virements ont été effectués."))

    def action_cancel(self):
        """Annuler le conseil"""
        self.write({'state': 'cancel'})
        self.message_post(body=_("Le conseil bancaire a été annulé."))

    def action_set_to_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft'})

    def action_view_payslips(self):
        """Voir les fiches de paie liées"""
        payslips = self.env['hr.payslip'].search([('advice_id', '=', self.id)])
        return {
            'name': _('Fiches de Paie'),
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', payslips.ids)],
            'context': {'create': False}
        }


class HrBankAdvice(models.Model):
    _inherit = 'hr.bank.advice'

    def generate_bank_export_file(self):
        self.ensure_one()

        # 1. Récupérer le RIB de la société pour la banque sélectionnée
        company_bank = self.env['res.partner.bank'].search([
            ('partner_id', '=', self.company_id.partner_id.id),
            ('bank_id', '=', self.bank_id.id)
        ], limit=1)

        if not company_bank:
            raise UserError(_("Aucun compte bancaire (RIB) n'est configuré pour la société '%s' à la banque '%s'.") % (
                self.company_id.name, self.bank_id.name))

        # Nettoyage du RIB (enlever espaces/tirets) et s'assurer qu'il fait 24 car.
        source_rib = (company_bank.acc_number or '').replace(' ', '').replace('-', '')
        if len(source_rib) < 16:  # Certains formats acceptent 16, mais le standard Maroc est 24
            source_rib = source_rib.zfill(16)

        date_str = self.date.strftime('%d%m%Y')
        lines = []

        # --- LIGNE D'ENTÊTE (0308) ---
        # Positions basées sur votre fichier texte
        company_name = (self.company_id.name or '')[:24].upper().ljust(24)

        header = "0308        000000    07"
        header += date_str
        header += company_name
        header += "       1125436                "  # Code fixe/ID de votre exemple
        header += source_rib.ljust(16)  # Dans votre exemple le RIB source fait 16
        header += " " * 47  # Espaces de remplissage
        header += "0000778038"  # Code fin entête
        lines.append(header)

        # --- LIGNES DE DÉTAILS (0608) ---
        sequence = 1
        total_amount = 0

        for line in self.line_ids:
            sequence_str = str(sequence).zfill(7)

            # Correction ici : on accède à .acc_number qui est la chaîne de caractères
            # On ajoute aussi une sécurité au cas où le compte n'est pas rempli
            raw_acc_number = line.account_number.acc_number if line.account_number else ''

            # Maintenant on peut faire le replace sur la string
            rib_benef = raw_acc_number.replace(' ', '').replace('-', '').zfill(24)

            # Le reste de votre logique...
            nom_beneficiaire = (line.employee_id.name or '')[:60].upper().ljust(60)

            # Montant formaté (ex: 850.00 -> 0000000000850000)
            amount_val = int(round(line.bysal * 100))
            amount_str = str(amount_val).zfill(16)

            # Construction de la ligne selon votre exemple
            detail = f"0608{date_str}{sequence_str}           "
            detail += nom_beneficiaire
            detail += rib_benef
            detail += amount_str
            detail += " " * 31  # Ajustez le nombre d'espaces selon votre besoin
            detail += "0002278074"

            lines.append(detail)
            total_amount += line.bysal
            sequence += 1

        # --- LIGNE DE PIED (0808) ---
        total_str = str(int(round(total_amount * 100))).zfill(12)
        # Structure de pied basée sur votre fichier : 0808 + espaces + total (position 90 environ)
        footer = "0808        000000"
        footer = footer.ljust(80) + total_str.zfill(22)
        lines.append(footer)

        # --- GÉNÉRATION DU FICHIER ---
        file_content = "\r\n".join(lines)  # Utilisation de CRLF pour Windows/Banques
        file_name = f"Virements_{self.bank_id.name}_{date_str}.txt"

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.b64encode(file_content.encode('utf-8')),
            'mimetype': 'text/plain',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class HrBankAdviceLine(models.Model):
    '''
    Lignes de Conseil Bancaire
    '''
    _name = 'hr.bank.advice.line'
    _description = 'Lignes de Conseil Bancaire'
    _order = 'employee_id'

    advice_id = fields.Many2one(
        'hr.bank.advice',
        string='Conseil Bancaire',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True
    )

    account_number = fields.Many2one(
        'res.partner.bank',
        string='Numéro de Compte',
        required=True
    )

    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Fiche de Paie'
    )

    bysal = fields.Monetary(
        string='Salaire Net',
        digits='Payroll',
        currency_field='currency_id'
    )

    debit_credit = fields.Char(
        string='D/C',
        default='C',
        help='Débit ou Crédit'
    )

    company_id = fields.Many2one(
        'res.company',
        related='advice_id.company_id',
        string='Société',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='advice_id.currency_id',
        string='Devise'
    )

    department_id = fields.Many2one(
        related='employee_id.department_id',
        string='Département',
        store=True
    )

    bank_name = fields.Char(
        related='account_number.bank_id.name',
        string='Nom de la Banque',
        store=True
    )

    @api.constrains('bysal')
    def _check_salary_amount(self):
        for line in self:
            if line.bysal <= 0:
                raise ValidationError(_('Le montant du salaire doit être positif.'))


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    advice_id = fields.Many2one(
        'hr.bank.advice',
        string='Conseil Bancaire',
        readonly=True
    )