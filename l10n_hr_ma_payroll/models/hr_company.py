# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import api, fields, models, _

class hr_contract(models.Model):
    _inherit = 'res.company'
    _description='Add fields for moroccan company'

    capital = fields.Monetary(
        string="Capital Social",
        required=False
    )
    rc = fields.Char(
        string="Registre de Commerce",
        required=False
    )
    tribunal = fields.Char(
        string="Tribunal RC",
        required=False
    )
    date_immat = fields.Date(
        string="Date d'immatriculation",
        required=False
    )
    ident_fiscal = fields.Char(
        string="Identifiant Fiscal",
        required=False
    )
    ice = fields.Char(
        string="I.C.E",
        required=False
    )
    patente_id = fields.Char(
        string="Patente ID",
        help="N° de la patente",
        copy=False,
        required=False
    )
    form_juridique = fields.Selection([
        ('seccursal_mar', 'Seccursal ou Agence Entreprise Marocaine'),
        ('seccursal_etr', 'Seccursal ou Agence Entreprise Etrangère'),
        ('societe_part', 'Société de Participation'),
        ('sa', 'Société Anonyme'),
        ('sarl', 'Société à Responsabilité Limitée'),
        ('sas', 'Société Anonyme Simplifiée'),
        ('sca', 'Société en Commandité par Action'),
        ('scs', 'Société en Commandité Simple'),
        ('seccursal_mar', 'Seccursal ou Agence Entreprise Marocaine'),
        ('scp', 'Société Civile Professionnelle'),
        ('snc', 'Société en Nom Collective'),
        ('sasimp', 'Société par Action Simplifiée')
    ], string='Forme Juridique', default='sarl')
    company_cnss_id = fields.Char(
        string="CNSS affiliation number",
        help="If the company is affiliated with the CNSS, include the CNSS number.",
        copy=False,
        required=False
    )
    cnss_limit = fields.Float(
        string="CNSS Base Salary Limit",
        help="Base salary ceiling for calculating the cnss",
        copy=False,
        default="6000"
    )
    employee_nbre = fields.Integer(
        string="Number of employees",
        copy=False,
        readonly=True,
        compute="_get_count_employee"
    )
    company_cimr_id = fields.Char(
        string="CIMR affiliation number",
        help="If the company is affiliated with the CIMR, include the CIMR number.",
        copy=False,
        required=False
    )

    def _get_count_employee(self):
        for emp in self:
            emp.employee_nbre = self.env['hr.employee'].search_count([('active', '=', True)])
