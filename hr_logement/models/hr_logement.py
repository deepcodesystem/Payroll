import time
from datetime import datetime,date
from dateutil import relativedelta
from odoo import models, fields, api, _


class EmployeeLogement(models.Model):
    _name = 'hr.logement'
    _description = 'HR Logement'

    contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    amount = fields.Float(string='Montant Interêt Log', required=True)
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), readonly=False)
    date_to = fields.Date(string='Date To',   readonly=False,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)