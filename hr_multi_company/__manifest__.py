# -*- coding: utf-8 -*-

{
    'name': 'Humain Ressources Multi-Company',
    'version': '17.0.1.5.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """Enables Multi-Company""",
    'description': 'This module enables multi company features',
    'author': 'GetapPRO',
    'company': 'GetapPRO',
    'maintainer': 'GetapPRO',
    'website': "https://www.getap.pro",
    'depends': ['payroll','l10n_hr_ma_payroll'],
    'data': [
        'security/multi_company_security.xml',
        'views/hr_payslip_run_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
