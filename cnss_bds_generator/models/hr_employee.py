# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ─── Champs CNSS ─────────────────────────────────────────────────────
    cnss_date_entree = fields.Date(
        string='Date d\'Entrée CNSS',
        groups='hr.group_hr_user',
    )
    cnss_statut = fields.Selection([
        ('actif', 'Actif'),
        ('sortant', 'Sortant'),
        ('nouveau', 'Nouveau (Entrant)'),
        ('occasionnel', 'Main d\'Œuvre Occasionnelle'),
    ], string='Statut CNSS', default='actif',
        groups='hr.group_hr_user',
    )

    @api.constrains('ssnid')
    def _check_cnss_num_assure(self):
        for rec in self:
            num = (rec.ssnid or '').strip()
            if not num:
                continue
            if num in ('000000000', '999999999'):
                continue
            if not self._validate_num_imma(num):
                raise ValidationError(
                    f"Le numéro d'immatriculation CNSS '{num}' de {rec.name} est invalide."
                )

    @staticmethod
    def _validate_num_imma(num):
        if not num or len(num) != 9 or not num.isdigit():
            return False
        if num[0] != '1' or num == '100000000':
            return False
        c = [int(x) for x in num]
        total = (c[1] + c[3] + c[5] + c[7]) * 2 + c[2] + c[4] + c[6]
        unite = total % 10
        cle = 0 if unite == 0 else (10 - unite)
        return cle == c[8]
