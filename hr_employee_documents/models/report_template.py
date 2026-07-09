# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression
from datetime import datetime


class HrEmployeeReportTemplate(models.Model):
    """Templates for employee documents/reports"""

    _name = 'hr.employee.report.template'
    _description = 'Employee Report Template'
    _order = 'sequence'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the document template'
    )
    code = fields.Char(
        string='Code',
        unique=True,
        help='Unique code for the template'
    )
    description = fields.Text(
        string='Description',
        help='Description of what this template generates'
    )
    report_type = fields.Selection(
        [
            ('work_certificate', 'Work Certificate (Attestation de travail)'),
            ('domicile_certificate', 'Domicile Certificate (Certificat de domiciliation)'),
            ('salary_certificate', 'Salary Certificate (Attestat ion de salaire)'),
            ('experience_certificate', 'Experience Certificate (Certificat d\'expérience)'),
            ('employment_history', 'Employment History (Historique d\'emploi)'),
            ('leave_balance', 'Leave Balance (Solde de congés)'),
            ('custom', 'Custom Report'),
        ],
        string='Report Type',
        required=True,
        default='custom'
    )

    # Template content
    template_content = fields.Html(
        string='Template Content',
        help='HTML template content with placeholders like {{employee.name}}, {{employee.job_title}}, etc.'
    )

    # Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in menu'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Permissions
    group_ids = fields.Many2many(
        'res.groups',
        string='Required Groups',
        help='If set, only users in these groups can access this template'
    )

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        domain = domain or []
        if not self.env.su and not self.env.user.has_group('hr.group_hr_manager'):
            domain = expression.AND([
                domain,
                ['|', ('group_ids', '=', False), ('group_ids', 'in', self.env.user.groups_id.ids)]
            ])
        return super().search(domain, offset=offset, limit=limit, order=order)

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}" if record.code else record.name
            result.append((record.id, name))
        return result
