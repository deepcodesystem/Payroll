# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CnssAffiliate(models.Model):
    _name = 'cnss.affiliate'
    _description = 'Affilié CNSS'
    _rec_name = 'num_affilie'

    # ─── Identification ───────────────────────────────────────────────────
    company_id = fields.Many2one(
        'res.company', string='Société', required=True,
        default=lambda self: self.env.company,
    )
    num_affilie = fields.Char(
        string='Numéro d\'affilié CNSS', size=7, required=True,
        help='Numéro d\'affiliation CNSS à 7 chiffres',
    )
    raison_sociale = fields.Char(
        string='Raison Sociale', size=40, required=True,
    )
    activite = fields.Char(
        string='Activité', size=40,
    )
    adresse = fields.Char(
        string='Adresse', size=120,
    )
    ville = fields.Char(
        string='Ville', size=20,
    )
    code_postal = fields.Char(
        string='Code Postal', size=6,
    )
    code_agence = fields.Char(
        string='Code Agence CNSS', size=2,
        help='Code de l\'agence CNSS (2 chiffres)',
    )
    active = fields.Boolean(default=True)
    note = fields.Text(string='Notes')

    # ─── Contraintes ──────────────────────────────────────────────────────
    _sql_constraints = [
        ('num_affilie_company_unique', 'UNIQUE(num_affilie, company_id)',
         'Le numéro d\'affilié CNSS doit être unique par société.'),
    ]

    @api.constrains('num_affilie')
    def _check_num_affilie(self):
        for rec in self:
            num = (rec.num_affilie or '').strip()
            if not num.isdigit() or len(num) != 7:
                raise ValidationError(
                    "Le numéro d'affilié CNSS doit contenir exactement 7 chiffres."
                )
            if not self._validate_num_affilie(num):
                raise ValidationError(
                    f"Le numéro d'affilié '{num}' est invalide (clé de contrôle incorrecte)."
                )

    @staticmethod
    def _validate_num_affilie(num):
        """
        Validation du numéro d'affilié CNSS selon l'algorithme du cahier des charges.
        C1..C7 : (C2+C4+C6)*2 + C1+C3+C5 → unités → si 0 alors clé=0 sinon 10-unités = C7
        """
        if len(num) != 7 or not num.isdigit():
            return False
        c = [int(x) for x in num]
        total = (c[1] + c[3] + c[5]) * 2 + c[0] + c[2] + c[4]
        unite = total % 10
        cle = 0 if unite == 0 else (10 - unite)
        return cle == c[6]

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.num_affilie} - {rec.raison_sociale}"
            result.append((rec.id, name))
        return result
