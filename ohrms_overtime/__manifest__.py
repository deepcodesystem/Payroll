# -- coding: utf-8 --
{
    'name': 'Payroll Overtime',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee overtime efficiently by tracking and analyzing.',
    'description': """This module provides a solution for streamline and 
    enhance the management of employee overtime within your organization. 
    This module empowers HR professionals and managers to efficiently track, 
    record, and analyze employee overtime""",
    'author': "GetapPRO",
    'company': 'GetapPRO',
    'maintainer': 'GetapPRO',
    'website': "https://www.getap.pro",
    'depends': ['hr_attendance', 'project', 'payroll', 'l10n_hr_ma_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'data/ir_sequence_data.xml',
        'views/hr_overtime_views.xml',
        'views/overtime_type_views.xml',
        #'views/hr_contract_views.xml',
        #'views/hr_payslip_views.xml',
    ],
    'demo': ['data/hr_overtime_demo.xml'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
