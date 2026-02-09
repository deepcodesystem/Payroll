# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime


class DocumentType(models.Model):
    """Categories/Types of employee documents"""

    _name = 'document.type'
    _description = 'Employee Document Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Document Type Name',
        required=True,
        translate=True,
        help='Name of the document type (e.g., Work Certificate, Experience Certificate)'
    )
    code = fields.Char(
        string='Code',
        required=True,
        unique=True,
        help='Unique code for the document type'
    )
    description = fields.Text(
        string='Description',
        translate=True,
        help='Detailed description of what this document type contains'
    )

    # Configuration
    require_manager_approval = fields.Boolean(
        string='Require Manager Approval',
        default=False,
        help='If checked, manager approval is required before employee can access'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this document type'
    )

    # Metadata
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order document types in lists'
    )
    color = fields.Integer(
        string='Color',
        help='Color indicator for this document type'
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Document type name must be unique!'),
        ('code_unique', 'UNIQUE(code)', 'Document type code must be unique!'),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"
            result.append((record.id, name))
        return result
