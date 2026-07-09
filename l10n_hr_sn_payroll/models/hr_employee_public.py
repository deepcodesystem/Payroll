from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    conjoint_salarie = fields.Boolean(readonly=True)
    quotient_familial = fields.Selection(readonly=True)
