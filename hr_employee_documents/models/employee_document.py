# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64


class EmployeeDocument(models.Model):
    """Employee documents (work certificates, attestations, etc.)"""

    _name = 'employee.document'
    _description = 'Employee Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date DESC'

    # Relations
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        help='The employee this document belongs to'
    )
    document_type_id = fields.Many2one(
        'document.type',
        string='Document Type',
        required=True,
        ondelete='restrict',
        help='Type of document'
    )
    created_by_id = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True,
        default=lambda self: self.env.user,
        help='User who uploaded this document'
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        compute='_compute_manager',
        store=True,
        readonly=True,
        help='The employee\'s manager'
    )

    # Document Information
    name = fields.Char(
        string='Document Title',
        required=True,
        translate=True,
        help='Title or name of the document'
    )
    description = fields.Text(
        string='Description',
        translate=True,
        help='Additional notes or description about this document'
    )

    # File Management
    document_file = fields.Binary(
        string='Document File',
        required=True,
        help='The document file (PDF, Word, etc.)'
    )
    file_name = fields.Char(
        string='File Name',
        compute='_compute_file_name',
        store=True,
        help='Name of the uploaded file'
    )
    file_size = fields.Integer(
        string='File Size (bytes)',
        readonly=True,
        help='Size of the document file'
    )
    file_type = fields.Char(
        string='File Type',
        compute='_compute_file_type',
        store=True,
        help='Type/Extension of the file'
    )

    # Dates
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        help='Date when the document was issued'
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        help='Date when the document expires (if applicable)'
    )
    upload_date = fields.Datetime(
        string='Upload Date',
        readonly=True,
        default=fields.Datetime.now,
        help='When the document was uploaded'
    )

    # Status & Approval
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        help='Current status of the document'
    )
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        help='When the document was approved'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help='Reason for rejection (if applicable)'
    )
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True,
        help='Whether the document has expired'
    )

    # Visibility & Access
    is_visible_to_employee = fields.Boolean(
        string='Visible to Employee',
        default=True,
        tracking=True,
        help='If checked, the employee can see this document'
    )

    # Additional Information
    reference_number = fields.Char(
        string='Reference Number',
        help='External reference or document ID'
    )
    notes = fields.Text(
        string='Internal Notes',
        help='Internal notes (not visible to employee)'
    )

    # Sequence for numbering
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order documents'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this document'
    )

    _sql_constraints = [
        ('name_not_empty', 'CHECK(name IS NOT NULL AND name != \'\')',
         'Document title cannot be empty!'),
    ]

    @api.depends('employee_id')
    def _compute_manager(self):
        """Compute the manager of the employee"""
        for record in self:
            if record.employee_id:
                record.manager_id = record.employee_id.parent_id
            else:
                record.manager_id = False

    @api.depends('document_file', 'name')
    def _compute_file_name(self):
        """Generate file name from context"""
        for record in self:
            if record.document_file and record.name:
                record.file_name = f"{record.name}_{record.id}"
            else:
                record.file_name = False

    @api.depends('file_name')
    def _compute_file_type(self):
        """Extract file type/extension"""
        for record in self:
            if record.file_name and '.' in str(record.file_name):
                record.file_type = record.file_name.split('.')[-1].upper()
            else:
                record.file_type = 'FILE'

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        """Check if document has expired"""
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiry_date and record.expiry_date < today

    @api.constrains('expiry_date', 'issue_date')
    def _check_dates(self):
        """Validate that expiry date is after issue date"""
        for record in self:
            if record.issue_date and record.expiry_date:
                if record.expiry_date < record.issue_date:
                    raise ValidationError(
                        _('Expiry date cannot be before issue date!')
                    )

    def action_submit_for_approval(self):
        """Submit document for manager approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    _('Only draft documents can be submitted for approval!')
                )
            record.write({'state': 'pending'})
        return True

    def action_approve(self):
        """Approve document"""
        for record in self:
            if record.state != 'pending':
                raise UserError(
                    _('Only pending documents can be approved!')
                )
            record.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
            })
        return True

    def action_reject(self):
        """Reject document - open wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.document.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_document_id': self.id,
            }
        }

    def action_reset_to_draft(self):
        """Reset document back to draft status"""
        for record in self:
            record.write({
                'state': 'draft',
                'approval_date': False,
                'rejection_reason': False,
            })
        return True

    def action_download(self):
        """Download the document file"""
        self.ensure_one()
        if not self.document_file:
            raise UserError(_('No file attached to this document!'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/document_file/{self.file_name}',
            'target': 'self',
        }

    def _get_file_extension(self):
        """Get the actual file extension"""
        if not self.document_file:
            return 'bin'
        # Try to guess from first few bytes
        try:
            header = base64.b64decode(self.document_file)[:4]
            if header.startswith(b'%PDF'):
                return 'pdf'
            elif header.startswith(b'PK'):
                return 'docx'
            elif header.startswith(b'\xff\xd8'):
                return 'jpg'
            elif header.startswith(b'\x89PNG'):
                return 'png'
        except:
            pass
        return 'bin'

    def create(self, vals_list):
        """Override create to set file size"""
        for vals in vals_list if isinstance(vals_list, list) else [vals_list]:
            if vals.get('document_file'):
                vals['file_size'] = len(base64.b64decode(vals['document_file']))
        return super().create(vals_list)

    def write(self, vals):
        """Override write to update file size when file changes"""
        if vals.get('document_file'):
            vals['file_size'] = len(base64.b64decode(vals['document_file']))
        return super().write(vals)

    @api.model
    def get_documents_by_type(self, employee_id, document_type_id):
        """Get documents by employee and type"""
        return self.search([
            ('employee_id', '=', employee_id),
            ('document_type_id', '=', document_type_id),
            ('active', '=', True),
        ], order='issue_date DESC')

    def action_view_employee_documents(self):
        """View all documents for this employee"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.document',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {
                'default_employee_id': self.employee_id.id,
            },
            'name': f'Documents - {self.employee_id.name}',
        }
