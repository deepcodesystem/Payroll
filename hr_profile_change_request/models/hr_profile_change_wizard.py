from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrProfileChangeWizard(models.TransientModel):
    _name = 'hr.profile.change.wizard'
    _description = 'Wizard de demande de modification du profil'

    employee_id = fields.Many2one('hr.employee', string='Employé', required=True,
        default=lambda self: self.env.user.employee_id)
    line_ids = fields.One2many('hr.profile.change.wizard.line', 'wizard_id', string='Champs')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee = self.env.user.employee_id
        if employee:
            res['employee_id'] = employee.id
            lines = []
            for field_key, field_label in self.env['hr.profile.change.request.line'].ALLOWED_FIELDS:
                field = self.env['hr.employee']._fields.get(field_key)
                if not field:
                    continue
                value = employee[field_key]
                current_value = self._format_value(value, field)
                lines.append((0, 0, {
                    'field_name': field_key,
                    'field_label': field_label,
                    'current_value': current_value,
                    'new_value': False,
                }))
            res['line_ids'] = lines
        return res

    def _format_value(self, value, field):
        if not value:
            return ''
        if field.type == 'many2one':
            return value.display_name
        if field.type == 'date':
            return str(value)
        if field.type == 'integer':
            return str(value)
        if field.type == 'selection':
            try:
                sel = field.selection
                if callable(sel):
                    sel = sel(self.env['hr.employee'])
                selection_dict = dict(sel)
                return selection_dict.get(value, str(value))
            except Exception:
                return str(value)
        return str(value)

    def action_submit(self):
        self.ensure_one()
        if not self.employee_id:
            raise UserError(_('Aucun employé lié à votre compte.'))

        changes = []
        for line in self.line_ids:
            if line.new_value and line.new_value != line.current_value:
                changes.append((0, 0, {
                    'field_name': line.field_name,
                    'old_value': line.current_value,
                    'new_value': line.new_value,
                }))

        if not changes:
            raise UserError(_('Veuillez modifier au moins un champ.'))

        request = self.env['hr.profile.change.request'].create({
            'employee_id': self.employee_id.id,
            'line_ids': changes,
        })
        request.action_submit()

        return {
            'type': 'ir.actions.act_window_close',
            'info': {'type': 'ir.actions.client', 'tag': 'display_notification',
                     'params': {'message': _('Votre demande a été soumise avec succès.'),
                                'type': 'success', 'sticky': False}},
        }
