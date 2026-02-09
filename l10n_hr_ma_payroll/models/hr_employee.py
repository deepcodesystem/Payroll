# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import api, fields, models, _
from datetime import date, datetime, time

class hr_contract(models.Model):
    _inherit = 'hr.employee'
    _description='Add fields for moroccan employee'

    dependants = fields.Integer(string='Nombre de dépendants', help='Nombre Total des personnes à charge pour le calcule de Paie')
    cimr_id = fields.Char(string='Numéro de CIMR', help='CIMR')
    cimr_date = fields.Date(string='Date CIMR', help='Date affiliation à la CIMR' )
    matricule = fields.Char(string='Matricule', help='Matricule')
    stc_settlement = fields.Boolean(
        string='Solde Tout Compte',
        default=False,
        help='Appliquer le calcul du Solde Tout Compte au dernier bulletin de paie'
    )

