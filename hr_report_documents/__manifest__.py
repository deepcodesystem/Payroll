# -*- coding: utf-8 -*-
{
    'name': 'Employee Document Reports',
    'version': '18.0.1.0.0',
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

    ],
    'demo': [],
    'external_dependencies': {
        'python': [],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
