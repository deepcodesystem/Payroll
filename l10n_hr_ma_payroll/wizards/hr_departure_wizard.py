# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    calculate_stc = fields.Boolean(
        string='Calculer Solde Tout Compte',
        default=False,
        help='Cocher pour appliquer le STC au dernier bulletin de paie'
    )

    stc_notes = fields.Text(
        string='Notes STC',
        help='Notes concernant le calcul du Solde Tout Compte'
    )

    @api.onchange('calculate_stc')
    def _onchange_calculate_stc(self):
        """Afficher un message d'information quand STC est sélectionné"""
        if self.calculate_stc:
            self.stc_notes = f"Le STC sera calculé pour {self.employee_id.name} au dernier bulletin de paie"
        else:
            self.stc_notes = ""

    def action_register_departure(self):
        """Enregistrer le départ et activer STC si coché"""
        _logger.info(f"Wizard départ pour {self.employee_id.name}, STC={self.calculate_stc}")

        if self.calculate_stc:
            # Vérifier que l'employé a un contrat actif
            if not self.employee_id.contract_id:
                raise UserError(
                    _('L\'employé n\'a pas de contrat actif.')
                )

            _logger.info(
                f"STC activé pour {self.employee_id.name} "
                f"- Date de départ: {self.departure_date}"
            )

        # Appeler l'action parent (qui mettra à jour le contrat avec la date de départ)
        result = super().action_register_departure()

        # Enregistrer le choix STC après l'action parent
        if self.calculate_stc:
            self.employee_id.write({
                'stc_settlement': True,
            })

            # Créer un log pour l'audit
            message_vals = {
                'model': 'hr.employee',
                'res_id': self.employee_id.id,
                'message_type': 'notification',
                'subtype_id': self.env.ref('mail.mt_note').id,
                'subject': _('Solde Tout Compte activé'),
                'body': _(
                    '<p><strong>Solde Tout Compte (STC)</strong> activé lors du départ de l\'employé.</p>'
                    '<p><strong>Date de départ:</strong> %(departure_date)s</p>'
                    '<p><strong>Motif:</strong> %(reason)s</p>'
                ) % {
                    'departure_date': self.departure_date,
                    'reason': self.departure_reason_id.name,
                }
            }

            try:
                self.env['mail.message'].create(message_vals)
                _logger.info(f"Message d'audit créé pour {self.employee_id.name}")
            except Exception as e:
                _logger.warning(f"Erreur lors de la création du message d'audit: {str(e)}")

        return result

