# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployeeExtend(models.Model):
    """Extend HR Employee model to add document relationship"""

    _inherit = 'hr.employee'

    document_ids = fields.One2many(
        'employee.document',
        'employee_id',
        string='Documents',
        help='Documents related to this employee'
    )

    documents_count = fields.Integer(
        string='Documents Count',
        compute='_compute_documents_count',
        help='Total number of documents for this employee'
    )

    pending_documents_count = fields.Integer(
        string='Pending Documents',
        compute='_compute_pending_documents_count',
        help='Number of pending documents for this employee'
    )

    def _compute_documents_count(self):
        """Count total documents"""
        for record in self:
            record.documents_count = len(record.document_ids)

    def _compute_pending_documents_count(self):
        """Count pending approval documents"""
        for record in self:
            record.pending_documents_count = len(
                record.document_ids.filtered(lambda d: d.state == 'pending')
            )

    def action_generate_employee_report(self):
        """Open report generation wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.report.template.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            }
        }

    def action_open_employee_documents(self):
        """Open employee documents"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.document',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
            },
            'name': _('Documents - %s') % self.name,
        }
