from odoo import fields, models


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_acc_number = fields.Char(
        string='Numéro de compte',
        related='bank_account_id.acc_number',
        readonly=False,
        help="Numéro de compte bancaire de l'employé",
    )
    employee_agence = fields.Char(
        string='Agence',
        related='bank_account_id.agence',
        readonly=False,
        help="Agence bancaire de l'employé",
    )
