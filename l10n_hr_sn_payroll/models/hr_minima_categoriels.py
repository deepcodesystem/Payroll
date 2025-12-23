# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import fields, models, api


class MinCategoriels(models.Model):
    _name = 'min.categoriels'
    _description='New model for categoriels minima'

    name = fields.Char(string="Catégorie", required=True)
    amount = fields.Monetary(string="Montant", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)