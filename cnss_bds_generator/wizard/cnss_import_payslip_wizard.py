# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CnssImportPayslipWizard(models.TransientModel):
    _name = 'cnss.import.payslip.wizard'
    _description = 'Assistant Import Bulletins de Paie → Déclaration CNSS'

    declaration_id = fields.Many2one(
        'cnss.declaration', string='Déclaration CNSS', required=True,
        readonly=True,
    )
    date_from = fields.Date(
        string='Période de début',
        required=True,
    )
    date_to = fields.Date(
        string='Période de fin',
        required=True,
    )
    # Plafond CNSS mensuel en centimes (6000 MAD = 600000 centimes)
    plafond_cnss = fields.Integer(
        string='Plafond CNSS (centimes)',
        default=600000,
        help='Plafond mensuel de cotisation CNSS en centimes (ex: 600000 = 6000 MAD)',
    )
    smig_mensuel = fields.Integer(
        string='SMIG Mensuel (centimes)',
        default=315893,
        help='SMIG mensuel en centimes pour contrôle (ex: 315893 ≈ 3158.93 MAD)',
    )

    # Codes de règles salariales OCA Maroc
    rule_code_sal_brut = fields.Char(
        string='Code Règle Salaire Brut', default='GROSS',
        help='Code de la règle salariale pour le salaire brut (ex: GROSS)',
    )

    line_ids = fields.One2many(
        'cnss.import.payslip.line', 'wizard_id',
        string='Lignes à importer',
    )
    state = fields.Selection([
        ('draft', 'Paramètres'),
        ('preview', 'Aperçu'),
    ], default='draft')

    @api.onchange('declaration_id')
    def _onchange_declaration_id(self):
        if self.declaration_id:
            decl = self.declaration_id
            year = decl.periode_annee
            month = int(decl.periode_mois)
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            from datetime import date
            self.date_from = date(year, month, 1)
            self.date_to = date(year, month, last_day)

    def action_preview(self):
        """Cherche les bulletins de paie et prépare les lignes d'aperçu."""
        self.ensure_one()
        domain = [
            ('state', 'in', ['done', 'paid']),
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
        ]
        if self.declaration_id.company_id:
            domain.append(('company_id', '=', self.declaration_id.company_id.id))

        payslips = self.env['hr.payslip'].search(domain)
        if not payslips:
            raise UserError(
                f"Aucun bulletin de paie validé trouvé pour la période "
                f"{self.date_from} - {self.date_to}."
            )

        # Supprimer les lignes existantes
        self.line_ids.unlink()

        lines = []
        for slip in payslips:
            emp = slip.employee_id
            num_assure = (getattr(emp, 'ssnid', '') or '').strip()
            cnss_statut = getattr(emp, 'cnss_statut', 'actif') or 'actif'
            situation = ''
            if cnss_statut == 'sortant':
                situation = 'SO'

            # Calcul salaire brut depuis les lignes de bulletin
            sal_brut = self._get_payslip_amount(slip, self.rule_code_sal_brut)
            if sal_brut == 0:
                # Fallback : chercher d'autres codes communs
                for code in ['BRUT', 'SBI', 'SALAIRE_BRUT', 'BASIC']:
                    sal_brut = self._get_payslip_amount(slip, code)
                    if sal_brut > 0:
                        break

            # Conversion en centimes
            sal_reel_centimes = int(round(sal_brut * 100))
            sal_plaf_centimes = min(sal_reel_centimes, self.plafond_cnss)

            # Nombre de jours (approximation basée sur la période)
            jours = self._compute_jours(slip)

            # AF depuis le bulletin si disponible
            af_payer = self._get_payslip_amount(slip, 'ALLFP') or 0
            af_payer_centimes = int(round(af_payer * 100))
            enfants = getattr(emp, 'dependants', 0) or 0

            lines.append({
                'wizard_id': self.id,
                'payslip_id': slip.id,
                'employee_id': emp.id,
                'num_assure': num_assure or '000000000',
                'nom_prenom': (emp.name or '').upper()[:60],
                'num_cin': (getattr(emp, 'identification_id', '') or '')[:8].upper(),
                'enfants': enfants,
                'jours': jours,
                'sal_reel': sal_reel_centimes,
                'sal_plaf': sal_plaf_centimes,
                'sal_reel_mad': sal_brut,
                'sal_plaf_mad': sal_plaf_centimes / 100.0,
                'af_a_payer': af_payer_centimes,
                'situation': situation,
                'cnss_statut': cnss_statut,
                'a_importer': True,
            })

        self.write({'line_ids': [(0, 0, l) for l in lines], 'state': 'preview'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_payslip_amount(self, slip, code):
        """Récupère le montant d'une règle salariale depuis un bulletin."""
        line = slip.line_ids.filtered(lambda l: l.code == code)
        if line:
            return abs(line[0].total)
        return 0.0

    def _compute_jours(self, slip):
        """Calcule le nombre de jours travaillés depuis le bulletin."""
        # Chercher d'abord un champ jours travaillés standard
        for code in ['JRTV', 'NJOURS', 'JOURS_TRAVAILLES', 'NB_JOURS']:
            jours = self._get_payslip_amount(slip, code)
            if jours > 0:
                return min(int(jours), 26)
        # Fallback sur les jours travaillés du bulletin
        worked = slip.worked_days_line_ids.filtered(
            lambda w: w.work_entry_type_id.is_leave == False
        )
        if worked:
            total_days = sum(w.number_of_days for w in worked)
            return min(int(total_days), 26)
        # Défaut = 26 jours
        return 26

    def action_import(self):
        """Importe les lignes sélectionnées dans la déclaration CNSS.

        Met à jour les lignes existantes (même num_assure) au lieu de créer des doublons.
        """
        self.ensure_one()
        decl = self.declaration_id
        lines_to_import = self.line_ids.filtered(lambda l: l.a_importer)
        if not lines_to_import:
            raise UserError("Aucune ligne sélectionnée pour l'import.")

        created_count = 0
        updated_count = 0

        for line in lines_to_import:
            if line.cnss_statut in ('nouveau', 'occasionnel'):
                # Entrants : vérifier si existe déjà
                existing_entrant = decl.entrant_ids.filtered(
                    lambda e: e.num_assure == line.num_assure or e.employee_id.id == line.employee_id.id
                )
                vals = {
                    'num_assure': line.num_assure,
                    'nom_prenom': line.nom_prenom,
                    'num_cin': line.num_cin,
                    'jours': line.jours,
                    'sal_reel': line.sal_reel,
                    'sal_plaf': line.sal_plaf,
                    'type_entrant': 'occasionnel' if line.cnss_statut == 'occasionnel' else 'normal',
                }
                if existing_entrant:
                    existing_entrant[0].write(vals)
                    updated_count += 1
                else:
                    vals.update({
                        'declaration_id': decl.id,
                        'employee_id': line.employee_id.id,
                    })
                    self.env['cnss.entrant'].create(vals)
                    created_count += 1
            else:
                # Existants : vérifier si ligne existe déjà (par num_assure ou employee_id)
                existing_line = decl.line_ids.filtered(
                    lambda l: l.num_assure == line.num_assure or
                    (l.employee_id and l.employee_id.id == line.employee_id.id)
                )
                vals = {
                    'num_assure': line.num_assure,
                    'nom_prenom': line.nom_prenom,
                    'jours': line.jours,
                    'sal_reel': line.sal_reel,
                    'sal_plaf': line.sal_plaf,
                    'situation': line.situation or '',
                }
                if existing_line:
                    # Mise à jour : conserver les infos AF existantes si présentes
                    if not existing_line[0].enfants and line.enfants:
                        vals['enfants'] = line.enfants
                    if not existing_line[0].af_a_payer and line.af_a_payer:
                        vals['af_a_payer'] = line.af_a_payer
                        vals['af_net_a_payer'] = line.af_a_payer - existing_line[0].af_a_deduire
                        vals['af_a_reverser'] = vals['af_net_a_payer']
                    existing_line[0].write(vals)
                    updated_count += 1
                else:
                    vals.update({
                        'declaration_id': decl.id,
                        'employee_id': line.employee_id.id,
                        'enfants': line.enfants,
                        'af_a_payer': line.af_a_payer,
                        'af_a_deduire': 0,
                        'af_net_a_payer': line.af_a_payer,
                        'af_a_reverser': line.af_a_payer,
                    })
                    self.env['cnss.declaration.line'].create(vals)
                    created_count += 1

        _logger.info(
            "Import bulletins CNSS: %d lignes créées, %d lignes mises à jour",
            created_count, updated_count
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cnss.declaration',
            'res_id': decl.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CnssImportPayslipLine(models.TransientModel):
    _name = 'cnss.import.payslip.line'
    _description = 'Ligne d\'aperçu import bulletins CNSS'

    wizard_id = fields.Many2one('cnss.import.payslip.wizard', ondelete='cascade')
    payslip_id = fields.Many2one('hr.payslip', string='Bulletin')
    employee_id = fields.Many2one('hr.employee', string='Employé')
    num_assure = fields.Char(string='N° Imma CNSS')
    nom_prenom = fields.Char(string='Nom & Prénom')
    num_cin = fields.Char(string='N° CIN')
    enfants = fields.Integer(string='Enfants AF')
    jours = fields.Integer(string='Jours')
    sal_reel = fields.Integer(string='Sal. Réel (cts)')
    sal_plaf = fields.Integer(string='Sal. Plaf. (cts)')
    sal_reel_mad = fields.Float(string='Sal. Réel (MAD)')
    sal_plaf_mad = fields.Float(string='Sal. Plaf. (MAD)')
    af_a_payer = fields.Integer(string='AF à Payer (cts)')
    situation = fields.Char(string='Situation')
    cnss_statut = fields.Char(string='Statut CNSS')
    a_importer = fields.Boolean(string='À Importer', default=True)
