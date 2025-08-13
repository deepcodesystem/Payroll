# -*- coding: utf-8 -*-

{
    'name': 'Payroll Advanced Features',
    'summary': 'Payroll Advanced Features For Odoo 17 Community.',
    'description': 'Payroll Advanced Features For Odoo 17 Community,'
                   'Payroll-Payslip Reporting, Automatic Mail During '
                   'Confirmation of Payslip, Mass Confirm Payslip ',
    'category': 'Generic Modules/Human Resources',
    'version': '17.0.2.1.0',
    'author': 'GetapPRO',
    'company': 'GetapPRO',
    'maintainer': 'GetapPRO',
    'website': 'https://www.getap.pro',
    'depends': [
        'payroll', 'mail', 'l10n_hr_ma_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_views.xml',
        'views/res_config_settings_views.xml',
        'data/mail_template_data.xml',
        'wizard/payslip_confirm_views.xml',
        'report/hr_payslip_report_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
