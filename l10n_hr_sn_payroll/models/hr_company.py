# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import api, fields, models, _

class hr_contract(models.Model):
    _inherit = 'res.company'
    _description='Add fields for moroccan company'

    company_css_id = fields.Char(
        string="CSS affiliation number",
        help="If the company is affiliated with the CSS, include the CSS number.",
        copy=False,
        required=False
    )
    ipres_gen_plaf = fields.Float(
        string="IPRES régime général Base Salary Limit",
        help="Base salary ceiling for calculating the IPRES régime général",
        copy=False,
        default="432000"
    )
    ipres_cad_plaf = fields.Float(
        string="IPRES régime cadre Base Salary Limit",
        help="Base salary ceiling for calculating the IPRES régime cadre",
        copy=False,
        default="296000"
    )
    css_af_plaf = fields.Float(
        string="CSS A.F. Base Salary Limit",
        help="Base salary ceiling for calculating the CSS Allocation Familiale",
        copy=False,
        default="63000"
    )
    css_at_plaf = fields.Float(
        string="CSS A.T Base Salary Limit",
        help="Base salary ceiling for calculating the CSS Accidents de Travail",
        copy=False,
        default="63000"
    )
    employee_nbre = fields.Integer(
        string="Number of employees",
        copy=False,
        readonly=True,
        compute="_get_count_employee"
    )

    def _get_count_employee(self):
        for emp in self:
            emp.employee_nbre = self.env['hr.employee'].search_count([('active', '=', True)])
