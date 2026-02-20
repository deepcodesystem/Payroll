# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    stc_settlement_id = fields.Many2one(
        'hr.stc.settlement',
        string='Enregistrement STC',
        readonly=True,
        copy=False
    )

    def _get_remaining_leaves(self, employee, date_to):
        """Calcul des jours de congés restants pour un employé"""
        allocation_obj = self.env['hr.leave.allocation']
        leave_obj = self.env['hr.leave']

        allocations = allocation_obj.search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            '|',
            ('date_to', '=', False),
            ('date_to', '>=', date_to),
        ])

        used_days = 0
        for allocation in allocations:
            leaves = leave_obj.search([
                ('holiday_allocation_id', '=', allocation.id),
                ('state', '=', 'validate'),
            ])
            used_days += sum(leave.number_of_days for leave in leaves)

        remaining_days = sum(allocation.number_of_days for allocation in allocations) - used_days
        return max(0, remaining_days)

    @api.model
    def _get_stc_amount(self, payslip, employee, contract):
        """Calcul du Solde Tout Compte (STC)"""
        if not employee.stc_settlement or not contract.date_end:
            return 0

        # Vérifier que c'est le dernier bulletin
        if contract.date_end != payslip.date_to:
            return 0

        # Base journalière
        base_journaliere = contract.wage / 26 if contract.wage else 0

        # Jours travaillés du mois
        worked_days = payslip.worked_days_line_ids.filtered(
            lambda x: x.work_entry_type_id.code == 'WORK100'
        )
        jours_travailles = sum(worked_days.mapped('number_of_days'))

        # Jours de congés restants
        jours_conges_restants = self._get_remaining_leaves(employee, payslip.date_to)

        # STC = (jours travaillés + jours congés restants) × base journalière
        stc_amount = (jours_travailles + jours_conges_restants) * base_journaliere

        return stc_amount

    def action_payslip_done(self):
        """Enregistrer automatiquement un STC si applicable"""
        result = super().action_payslip_done()

        for payslip in self:
            employee = payslip.employee_id
            contract = payslip.contract_id

            # Vérifier si un STC doit être créé
            if (employee.stc_settlement and contract.date_end
                and contract.date_end == payslip.date_to
                and not payslip.stc_settlement_id):

                # Calculer le montant STC
                stc_amount = self._get_stc_amount(payslip, employee, contract)

                if stc_amount > 0:
                    # Récupérer les jours travaillés
                    worked_days_lines = payslip.worked_days_line_ids.filtered(
                        lambda x: x.work_entry_type_id.code == 'WORK100'
                    )
                    jours_travailles = sum(worked_days_lines.mapped('number_of_days'))

                    # Récupérer les jours de congés restants
                    jours_conges = self._get_remaining_leaves(employee, payslip.date_to)

                    # Base journalière
                    base_journaliere = contract.wage / 26 if contract.wage else 0

                    # Créer l'enregistrement STC
                    stc_settlement = self.env['hr.stc.settlement'].create({
                        'employee_id': employee.id,
                        'payslip_id': payslip.id,
                        'stc_amount': stc_amount,
                        'worked_days': jours_travailles,
                        'remaining_leaves': jours_conges,
                        'daily_rate': base_journaliere,
                        'notes': f"STC calculé automatiquement pour {employee.name}",
                    })

                    # Lier le bulletin au STC
                    payslip.stc_settlement_id = stc_settlement

        return result

    def get_inputs(self, contract_ids, date_from, date_to):
        """Supering get_inputs() method inorder to add details of advance
           salary in the payslip."""
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from,
                                                date_to)
        epargne_amount = self.contract_id.epargne_retraite if self.contract_id.epargne_retraite else 0
        epargne_ir_amount = self.contract_id.epargne_retraite_ir if self.contract_id.epargne_retraite_ir else 0
        for result in res:
            if result.get('code') == 'EPARGNE':
                result['amount'] = epargne_amount
            elif result.get('code') == 'EPARGNEIR':
                result['amount'] = epargne_ir_amount
        return res

