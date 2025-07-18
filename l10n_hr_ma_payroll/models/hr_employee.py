# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import api, fields, models, _

class hr_contract(models.Model):
    _inherit = 'hr.employee'
    _description='Add fields for moroccan employee'

    dependants = fields.Integer(string='Nombre de dépendants', help='Nombre Total des personnes à charge pour le calcule de Paie')
    cimr_id = fields.Char(string='Numéro de CIMR', help='CIMR')
    matricule = fields.Char(string='Matricule', help='Matricule')

