# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class LogementRuleInput(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(LogementRuleInput, self).get_inputs(contract_ids, date_from, date_to)
        contract_id = self.contract_id.id
        log_salary = self.env['hr.logement'].search([('contract_id', '=', contract_id)])
        for log_obj in log_salary:
            current_date = date_from
            date = log_obj.date_from
            if current_date == date:
                amount = log_obj.amount
                for result in res:
                    if amount != 0 and result.get('code') == 'LOG':
                        result['amount'] = amount
        return res