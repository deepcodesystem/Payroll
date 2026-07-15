{
    'name': 'HR Profile Change Request',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': "Demande de modification du profil RH avec validation",
    'description': """
HR Profile Change Request
==========================

Permet aux employés de soumettre des demandes de modification
de leur profil RH. Les demandes sont validées par un responsable RH.

Fonctionnalités :
- L'employé sélectionne le champ à modifier et saisit la nouvelle valeur
- Le RH voit l'ancienne et la nouvelle valeur
- Approbation ou refus avec commentaire
- Écriture automatique sur hr.employee lors de l'approbation
- Notifications par messagerie Odoo
    """,
    'author': 'DeepCode',
    'website': 'https://deeposapps.com',
    'depends': ['hr', 'l10n_hr_ma_payroll'],
    'data': [
        'security/hr_profile_change_request_security.xml',
        'security/ir.model.access.csv',
        'data/mail_message_subtype_data.xml',
        'views/hr_profile_change_request_views.xml',
        'views/hr_profile_change_wizard_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_profile_change_request_menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
