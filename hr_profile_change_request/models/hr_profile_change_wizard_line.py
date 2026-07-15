from odoo import fields, models


class HrProfileChangeWizardLine(models.TransientModel):
    _name = 'hr.profile.change.wizard.line'
    _description = 'Ligne du wizard de modification du profil'

    wizard_id = fields.Many2one('hr.profile.change.wizard', string='Wizard', required=True, ondelete='cascade')
    field_name = fields.Char(string='Champ', readonly=True)
    field_label = fields.Char(string='Libellé', readonly=True)
    current_value = fields.Char(string='Valeur actuelle', readonly=True)
    new_value = fields.Char(string='Nouvelle valeur')
