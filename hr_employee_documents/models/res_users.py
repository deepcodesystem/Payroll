# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResUsersExtend(models.Model):
    """Extend Res Users model to add document relationship"""

    _inherit = 'res.users'

    def action_generate_employee_report(self):
        """Open report generation wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.report.template.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.employee_id.id,
            }
        }

    def action_open_employee_documents(self):
        """Open employee documents"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.document',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {
                'default_employee_id': self.employee_id.id,
            },
            'name': _('Documents - %s') % self.name,
        }
