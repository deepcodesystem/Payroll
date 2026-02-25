# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

SITUATION_LABELS = [
    ('', 'Normale (travail effectif)'),
    ('SO', 'SO - Sortant'),
    ('DE', 'DE - Décédé'),
    ('IT', 'IT - Maternité'),
    ('IL', 'IL - Maladie'),
    ('AT', 'AT - Accident de Travail'),
    ('CS', 'CS - Congé Sans Salaire'),
    ('MS', 'MS - Maintenu Sans Salaire'),
    ('MP', 'MP - Maladie Professionnelle'),
]


class CnssDeclarationLine(models.Model):
    _name = 'cnss.declaration.line'
    _description = 'Ligne Déclaration CNSS - Assuré Existant (Préétabli)'
    _order = 'num_assure'

    declaration_id = fields.Many2one(
        'cnss.declaration', string='Déclaration', required=True,
        ondelete='cascade', index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employé',
        help='Lien vers l\'employé Odoo (optionnel)',
    )

    # ─── Données préétabli (viennent de la CNSS) ─────────────────────────
    num_assure = fields.Char(
        string='N° Immatriculation CNSS', size=9, required=True,
        help='Numéro d\'immatriculation CNSS à 9 chiffres',
    )
    nom_prenom = fields.Char(
        string='Nom & Prénom', size=60, required=True,
    )
    enfants = fields.Integer(
        string='Nb Enfants (AF)', default=0,
        help='Nombre d\'enfants donnant droit aux allocations familiales',
    )
    af_a_payer = fields.Integer(
        string='AF à Payer (centimes)', default=0,
        help='Montant AF dues au titre du mois, à payer (en centimes)',
    )
    af_a_deduire = fields.Integer(
        string='AF à Déduire (centimes)', default=0,
        help='Montant AF perçues en trop, à déduire (en centimes)',
    )
    af_net_a_payer = fields.Integer(
        string='AF Net à Payer (centimes)', default=0,
        compute='_compute_af_net', store=True,
        help='Montant AF net à payer = AF à payer - AF à déduire (en centimes)',
    )

    # ─── Données saisies par l'affilié ────────────────────────────────────
    af_a_reverser = fields.Integer(
        string='AF à Reverser (centimes)', default=0,
        help='Montant AF à reverser à la CNSS (≤ AF net à payer, en centimes)',
    )
    jours = fields.Integer(
        string='Jours Déclarés', default=0,
        help='Nombre de jours travaillés (0 à 26)',
    )
    sal_reel = fields.Integer(
        string='Salaire Réel (centimes)', default=0,
        help='Salaire brut réel non plafonné (en centimes)',
    )
    sal_plaf = fields.Integer(
        string='Salaire Plafonné (centimes)', default=0,
        help='Salaire dans la limite du plafond CNSS (en centimes)',
    )
    situation = fields.Selection(
        SITUATION_LABELS,
        string='Situation', default='',
        help='Situation de l\'assuré ce mois',
    )

    # ─── Champs calculés d'affichage ─────────────────────────────────────
    sal_reel_mad = fields.Float(
        string='Salaire Réel (MAD)', compute='_compute_mad', store=False,
    )
    sal_plaf_mad = fields.Float(
        string='Salaire Plafonné (MAD)', compute='_compute_mad', store=False,
    )
    af_a_payer_mad = fields.Float(
        string='AF à Payer (MAD)', compute='_compute_mad', store=False,
    )
    af_a_reverser_mad = fields.Float(
        string='AF à Reverser (MAD)', compute='_compute_mad', store=False,
    )
    ctr = fields.Integer(
        string='Contrôle Horizontal', compute='_compute_ctr', store=True,
    )

    @api.depends('af_a_payer', 'af_a_deduire')
    def _compute_af_net(self):
        for rec in self:
            rec.af_net_a_payer = max(0, (rec.af_a_payer or 0) - (rec.af_a_deduire or 0))

    @api.depends('sal_reel', 'sal_plaf', 'af_a_payer', 'af_a_reverser')
    def _compute_mad(self):
        for rec in self:
            rec.sal_reel_mad = (rec.sal_reel or 0) / 100.0
            rec.sal_plaf_mad = (rec.sal_plaf or 0) / 100.0
            rec.af_a_payer_mad = (rec.af_a_payer or 0) / 100.0
            rec.af_a_reverser_mad = (rec.af_a_reverser or 0) / 100.0

    @api.depends('num_assure', 'af_a_reverser', 'jours', 'sal_reel', 'sal_plaf', 'situation')
    def _compute_ctr(self):
        from .cnss_declaration import SITUATION_RANG
        for rec in self:
            sit = (rec.situation or '').strip().upper()
            rang = SITUATION_RANG.get(sit if sit else '  ', 0)
            rec.ctr = (
                    int(rec.num_assure or 0) +
                    int(rec.af_a_reverser or 0) +
                    int(rec.jours or 0) +
                    int(rec.sal_reel or 0) +
                    int(rec.sal_plaf or 0) +
                    rang
            )

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Remplissage auto depuis l'employé."""
        if self.employee_id:
            emp = self.employee_id
            self.nom_prenom = (emp.name or '').upper()[:60]
            if hasattr(emp, 'ssnid') and emp.ssnid:
                self.num_assure = emp.ssnid
            if hasattr(emp, 'dependants'):
                self.enfants = emp.dependants or 0

    @api.onchange('situation')
    def _onchange_situation(self):
        """Réinitialise les champs selon la situation."""
        sit = (self.situation or '').strip().upper()
        if sit in ('CS', 'MS'):
            self.jours = 0
            self.sal_reel = 0
            self.sal_plaf = 0
        if sit in ('SO', 'DE'):
            self.af_a_reverser = self.af_net_a_payer

    @api.constrains('jours')
    def _check_jours(self):
        for rec in self:
            if rec.jours < 0 or rec.jours > 26:
                raise ValidationError(
                    f"Le nombre de jours doit être entre 0 et 26 (assuré {rec.num_assure})."
                )

    @api.constrains('sal_plaf', 'sal_reel')
    def _check_salaires(self):
        for rec in self:
            if rec.sal_plaf > rec.sal_reel:
                raise ValidationError(
                    f"Le salaire plafonné ne peut pas dépasser le salaire réel (assuré {rec.num_assure})."
                )

    @api.constrains('af_a_reverser', 'af_net_a_payer')
    def _check_af_reverser(self):
        for rec in self:
            if rec.af_a_reverser > rec.af_net_a_payer:
                raise ValidationError(
                    f"L'AF à reverser ({rec.af_a_reverser}) ne peut pas dépasser l'AF net à payer "
                    f"({rec.af_net_a_payer}) pour l'assuré {rec.num_assure}."
                )