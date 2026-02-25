# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CnssEntrant(models.Model):
    _name = 'cnss.entrant'
    _description = 'Assuré Entrant CNSS'
    _order = 'num_assure'

    declaration_id = fields.Many2one(
        'cnss.declaration', string='Déclaration', required=True,
        ondelete='cascade', index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employé',
        help='Lien vers l\'employé Odoo (optionnel)',
    )

    # ─── Identification ───────────────────────────────────────────────────
    num_assure = fields.Char(
        string='N° Immatriculation CNSS', size=9,
        help='9 chiffres. Laisser vide ou 000000000 si non immatriculé. '
             '999999999 pour main d\'œuvre occasionnelle.',
        default='000000000',
    )
    nom_prenom = fields.Char(
        string='Nom & Prénom', size=60, required=True,
        help='Uniquement caractères ASCII majuscules (A-Z, 0-9, espace)',
    )
    num_cin = fields.Char(
        string='N° CIN', size=8,
        help='Numéro de la Carte d\'Identité Nationale (obligatoire si pas de n° imma)',
    )
    type_entrant = fields.Selection([
        ('normal', 'Entrant Normal'),
        ('occasionnel', 'Main d\'Œuvre Occasionnelle'),
    ], string='Type', default='normal', required=True)

    # ─── Données de paie ─────────────────────────────────────────────────
    jours = fields.Integer(
        string='Jours Travaillés', default=26,
        help='Nombre de jours travaillés (1 à 26)',
    )
    sal_reel = fields.Integer(
        string='Salaire Réel (centimes)', default=0,
        help='Salaire brut réel non plafonné (en centimes)',
    )
    sal_plaf = fields.Integer(
        string='Salaire Plafonné (centimes)', default=0,
        help='Salaire dans la limite du plafond CNSS (en centimes)',
    )

    # ─── Affichage MAD ───────────────────────────────────────────────────
    sal_reel_mad = fields.Float(
        string='Salaire Réel (MAD)', compute='_compute_mad', store=False,
    )
    sal_plaf_mad = fields.Float(
        string='Salaire Plafonné (MAD)', compute='_compute_mad', store=False,
    )
    ctr = fields.Integer(
        string='Contrôle Horizontal', compute='_compute_ctr', store=True,
    )

    @api.depends('sal_reel', 'sal_plaf')
    def _compute_mad(self):
        for rec in self:
            rec.sal_reel_mad = (rec.sal_reel or 0) / 100.0
            rec.sal_plaf_mad = (rec.sal_plaf or 0) / 100.0

    @api.depends('num_assure', 'jours', 'sal_reel', 'sal_plaf')
    def _compute_ctr(self):
        for rec in self:
            num = int((rec.num_assure or '0').strip() or '0')
            rec.ctr = (
                num +
                int(rec.jours or 0) +
                int(rec.sal_reel or 0) +
                int(rec.sal_plaf or 0)
            )

    @api.onchange('type_entrant')
    def _onchange_type_entrant(self):
        if self.type_entrant == 'occasionnel':
            self.num_assure = '999999999'
            self.jours = 0

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            emp = self.employee_id
            self.nom_prenom = (emp.name or '').upper()[:60]
            if hasattr(emp, 'cnss_num_assure') and emp.cnss_num_assure:
                self.num_assure = emp.cnss_num_assure
            if hasattr(emp, 'id_number'):
                self.num_cin = (emp.id_number or '')[:8].upper()

    @api.constrains('jours', 'type_entrant')
    def _check_jours(self):
        for rec in self:
            if rec.type_entrant == 'normal':
                if rec.jours <= 0 or rec.jours > 26:
                    raise ValidationError(
                        f"Entrant {rec.nom_prenom} : jours doit être entre 1 et 26."
                    )

    @api.constrains('sal_plaf', 'sal_reel')
    def _check_salaires(self):
        for rec in self:
            if rec.sal_plaf > rec.sal_reel:
                raise ValidationError(
                    f"Entrant {rec.nom_prenom} : salaire plafonné > salaire réel."
                )

    @api.constrains('num_cin', 'num_assure')
    def _check_cin(self):
        for rec in self:
            num = (rec.num_assure or '').strip()
            if num == '000000000' or not num:
                if not (rec.num_cin or '').strip():
                    raise ValidationError(
                        f"Entrant {rec.nom_prenom} : le N° CIN est obligatoire si pas de n° immatriculation."
                    )
