# -*- coding: utf-8 -*-
{
    'name': 'Payslip Logement Calcul IR Maroc',
    'version': '18.0.15.1.0',
    'summary': """Employee Interet Logement Principal pour la Paie Maroc.""",
    'description': """Gestion des intérêts Logement Principal pour la Paie Maroc.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'WAHBI ACHRAF',
    'maintainer': 'PINTFORGE',
    'company': 'PINTFORGE',
    'website': 'https://www.pintforge.com',
    'depends': [
                'hr','payroll','l10n_hr_ma_payroll'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/logement_salary_stucture.xml',
              ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
