# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeDocumentRejectWizard(models.TransientModel):
    """Wizard for rejecting employee documents"""

    _name = 'employee.document.reject.wizard'
    _description = 'Reject Employee Document'

    document_id = fields.Many2one(
        'employee.document',
        string='Document',
        required=True,
        ondelete='cascade'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
        placeholder='Please explain why this document is being rejected...'
    )
    notify_employee = fields.Boolean(
        string='Notify Employee',
        default=True,
        help='Send notification to employee about the rejection'
    )

    def action_reject(self):
        """Reject the document"""
        self.ensure_one()

        if not self.rejection_reason:
            raise UserError(_('Please provide a rejection reason!'))

        self.document_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })

        if self.notify_employee:
            # Send notification via chatter
            self.document_id.message_post(
                body=_('Document has been rejected.\n\nReason: %s') % self.rejection_reason,
                message_type='notification'
            )

        return {
            'type': 'ir.actions.act_window_close'
        }
