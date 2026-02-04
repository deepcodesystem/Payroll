# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EmployeeDocumentReport(models.AbstractModel):
    """Report for employee documents"""

    _name = 'report.hr_employee_documents.employee_document_report'
    _description = 'Employee Document Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Generate report values"""
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'hr_employee_documents.employee_document_report'),
        ], limit=1)

        documents = self.env['employee.document'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'employee.document',
            'docs': documents,
            'report': report,
            'get_status_display': self._get_status_display,
        }

    @staticmethod
    def _get_status_display(state):
        """Get display name for status"""
        states = {
            'draft': 'Draft',
            'pending': 'Pending Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
        }
        return states.get(state, state)
