# -*- coding: utf-8 -*-
{
    'name': 'Employee Document Management',
    'version': '18.0.3.23.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Manage and download employee documents like work certificates, attestations, etc.',
    'description': """
        This module provides a solution for managers to upload, manage and download 
        employee documents such as:
        - Work Certificates (Attestation de travail)
        - Experience Certificates
        - Medical Records
        - Training Certificates
        - And other HR documents
        
        Features:
        - Upload documents by managers/HR staff
        - Organize documents by type and employee
        - Access control and permissions
        - Document version history
        - Bulk document generation
    """,
    'author': 'GetapPRO',
    'company': 'GetapPRO',
    'maintainer': 'GetapPRO',
    'website': 'https://www.getap.pro',
    'depends': ['hr', 'hr_contract', 'payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/document_type_data.xml',
        'data/report_template_data.xml',
        'views/document_type_views.xml',
        'views/employee_document_views.xml',
        'views/reject_wizard_views.xml',
        'views/hr_employee_views.xml',
        'views/report_template_views.xml',
        'views/report_generator_views.xml',
        'views/employee_report_buttons.xml',
        'reports/report.xml',
        'reports/employee_document_report.xml',
        'reports/employee_document_qweb.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'external_dependencies': {
        'python': [],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
