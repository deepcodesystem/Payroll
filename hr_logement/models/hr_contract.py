# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'

    logement = fields.One2many('hr.logement', 'contract_id', string="Interêt Logement Principal")
