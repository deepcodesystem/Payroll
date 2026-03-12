# -*- coding: utf-8 -*-
from odoo import api, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = super().get_inputs(contracts, date_from, date_to)
        for contract in contracts:
            if contract.forfait_hs:
                for result in res:
                    if result.get('code') == 'FORHS' and result.get('contract_id') == contract.id:
                        result['amount'] = contract.forfait_hs
        return res