# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    conjoint_salarie = fields.Boolean(
        string="Situation Salariale Conjoint",
        default=False,
        help="Cocher si le conjoint du salarié dispose de revenus salariaux"
    )
    quotient_familial = fields.Selection(
        selection=[
            ('1', '1'),
            ('1.5', '1,5'),
            ('2', '2'),
            ('2.5', '2,5'),
            ('3', '3'),
        ],
        string="Quotient Familial",
        default='1',
        help="Nombre de parts fiscales du salarié"
    )

    @api.onchange('marital')
    def _onchange_marital_conjoint(self):
        if self.marital != 'married':
            self.conjoint_salarie = False
