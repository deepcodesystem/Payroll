# -*- coding: utf-8 -*-
from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    salary_net = fields.Monetary('Salary Net', tracking=True, help="Employee's monthly net salary.")
