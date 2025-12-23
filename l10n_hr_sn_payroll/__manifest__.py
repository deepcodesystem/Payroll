{
    'name': 'Paie Sénégal 2025',
    'description': 'Configuration de la paie Sénégalaise pour 2025',
    'category': 'Humain Ressources',
    'version': '18.0.1.0.0',
    'depends': ['hr', 'hr_contract', 'payroll'],
    'data': [
        'data/l10n_sn_payroll_data.xml',
        'data/min_categoriels_data.xml',
        'security/ir.model.access.csv',
        'views/hr_company_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_minima_categ_views.xml',
        'views/bank_advice_views.xml',
    ],
    'license': 'LGPL-3',
}
