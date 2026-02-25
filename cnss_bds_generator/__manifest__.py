# -*- coding: utf-8 -*-
{
    'name': 'CNSS BDS - Télédéclaration Maroc',
    'version': '18.0.1.0.0',
    'category': 'Payroll/Morocco',
    'summary': 'Génération des fichiers BDS CNSS pour la télédéclaration (portail Damancom)',
    'description': """
CNSS BDS - Télédéclaration Maroc
=================================
Module de génération des fichiers BDS (Bordereau de Déclaration des Salaires)
conformément au cahier des charges CNSS v2 / Février 2006.

Fonctionnalités :
-----------------
- Saisie des informations affilié (numéro CNSS, agence, etc.)
- Déclaration des assurés existants (préétabli)
- Déclaration des assurés entrants
- Génération du fichier BDS principal (DS_NNNNNNN_MMAAAA.txt)
- Génération du fichier BDS complémentaire (DSC[N]_NNNNNNN_MMAAAA.txt)
- Contrôles de cohérence (totaux horizontaux et verticaux)
- Validation des numéros d'immatriculation CNSS
- Validation des numéros d'affilié
- Support des situations : SO, DE, IT, IL, AT, CS, MS, MP
- Intégration avec le module payroll OCA (l10n_ma_payroll)
    """,
    'author': 'Damancom',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'payroll',
        'l10n_hr_ma_payroll',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/cnss_bds_security.xml',
        'views/cnss_affiliate_views.xml',
        'views/cnss_declaration_views.xml',
        'views/cnss_declaration_line_views.xml',
        'views/cnss_entrant_views.xml',
        'views/menu_views.xml',
        'views/hr_employee_views.xml',
        'wizard/cnss_import_payslip_wizard_views.xml',
        'data/cnss_data.xml',
    ],
    #'assets': {
    #    'web.assets_backend': [
    #        'cnss_bds_generator/static/src/css/cnss_style.css',
    #    ],
    #},
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
