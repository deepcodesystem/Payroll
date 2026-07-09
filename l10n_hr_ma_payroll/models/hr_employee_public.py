from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    dependants = fields.Integer(readonly=True)
    cimr_id = fields.Char(readonly=True)
    cimr_date = fields.Date(readonly=True)
    matricule = fields.Char(readonly=True)
    stc_settlement = fields.Boolean(readonly=True)
