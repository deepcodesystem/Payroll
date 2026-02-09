# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartnerBankExtend(models.Model):
    """Extend Res Bank model to add document relationship"""
    _inherit = 'res.partner.bank'
    _description = 'Res Partner Bank Extend'

    agence = fields.Char(string='Agence', help='Bank agency name or number')