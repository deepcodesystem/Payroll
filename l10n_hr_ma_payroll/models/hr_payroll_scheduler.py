# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime, timedelta

class HrPayrollScheduler(models.Model):
    _name = 'hr.payroll.scheduler'
    _description = 'Gestionnaire de paie planifiée'

    @api.model
    def _cron_generate_settlement_payslips(self):
        """Génère les feuilles de sortie pour employés archivés"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        domain = [
            ('company_id', '=', self.env.company.id),
            ('contract_ids.date_end', '<=', month_end),
            ('contract_ids.date_end', '>=', month_start),
            ('active', '=', False),
        ]

        employees = self.env['hr.employee'].search(domain)

        for employee in employees:
            contract = employee.contract_id
            if not contract or contract.date_end > month_end:
                continue
