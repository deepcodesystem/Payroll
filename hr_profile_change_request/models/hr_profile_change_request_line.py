from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrProfileChangeRequestLine(models.Model):
    _name = 'hr.profile.change.request.line'
    _description = 'Ligne de modification du profil RH'

    ALLOWED_FIELDS = [
        ('private_street', 'Adresse privée'),
        ('private_street2', 'Adresse privée 2'),
        ('private_city', 'Ville'),
        ('private_state_id', 'État / Province'),
        ('private_zip', 'Code postal'),
        ('private_country_id', 'Pays'),
        ('private_email', 'Email privé'),
        ('private_phone', 'Téléphone privé'),
        ('private_lang', 'Langue'),
        ('employee_bank_account_id', 'Compte bancaire'),
        ('distance_home_work', 'Distance domicile-travail'),
        ('distance_home_work_unit', 'Unité de distance'),
        ('employee_country_id', 'Nationalité'),
        ('identification_id', "Numéro d'identification"),
        ('ssnid', 'Numéro de sécurité sociale'),
        ('cimr_id', 'Numéro CIMR'),
        ('cimr_date', 'Date CIMR'),
        ('passport_id', 'Numéro de passeport'),
        ('gender', 'Genre'),
        ('birthday', 'Date de naissance'),
        ('place_of_birth', 'Lieu de naissance'),
        ('country_of_birth', 'Pays de naissance'),
        ('marital', 'État civil'),
        ('spouse_complete_name', 'Nom du conjoint'),
        ('spouse_birthdate', 'Date de naissance du conjoint'),
        ('children', 'Nombre d\'enfants'),
        ('dependants', 'Nombre de personnes à charge'),
        ('certificate', 'Niveau d\'étude'),
        ('study_field', 'Domaine d\'étude'),
        ('study_school', 'Établissement'),
        ('emergency_contact', 'Contact d\'urgence'),
        ('emergency_phone', 'Téléphone d\'urgence'),
        ('visa_no', 'Numéro de visa'),
        ('permit_no', 'Numéro de permis'),
        ('visa_expire', 'Expiration du visa'),
    ]

    request_id = fields.Many2one('hr.profile.change.request', string='Demande',
        required=True, ondelete='cascade', readonly=True)
    employee_id = fields.Many2one('hr.employee', related='request_id.employee_id', store=True)
    company_id = fields.Many2one('res.company', related='request_id.company_id', store=True)
    state = fields.Selection(related='request_id.state', store=True)
    field_name = fields.Selection(selection=ALLOWED_FIELDS, string='Champ', required=True)
    field_label = fields.Char(string='Libellé du champ', compute='_compute_field_label', store=True)
    old_value = fields.Char(string='Valeur actuelle', readonly=True)
    new_value = fields.Char(string='Nouvelle valeur', required=True)

    @api.depends('field_name')
    def _compute_field_label(self):
        allowed_dict = dict(self.ALLOWED_FIELDS)
        employee_fields = self.env['hr.employee']._fields
        for rec in self:
            label = allowed_dict.get(rec.field_name, rec.field_name)
            if rec.field_name in employee_fields:
                label = employee_fields[rec.field_name].string
            rec.field_label = label

    @api.onchange('field_name')
    def _onchange_field_name(self):
        if not self.field_name or not self.employee_id:
            self.old_value = False
            self.new_value = False
            return
        field = self.env['hr.employee']._fields.get(self.field_name)
        if not field:
            return
        value = self.employee_id[self.field_name]
        self.old_value = self._format_value(value, field)
        self.new_value = False

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

    def _convert_to_field_type(self, value_str, field):
        if not value_str:
            return False
        if field.type in ('char', 'text'):
            return value_str
        if field.type == 'integer':
            try:
                return int(value_str)
            except (ValueError, TypeError):
                return 0
        if field.type == 'date':
            try:
                return fields.Date.from_string(value_str)
            except (ValueError, TypeError):
                return False
        if field.type == 'many2one':
            return self._resolve_many2one(value_str, field)
        if field.type == 'selection':
            selection_dict = dict(field.selection)
            for key, label in selection_dict.items():
                if label == value_str or key == value_str:
                    return key
            return value_str
        return value_str

    def _resolve_many2one(self, value_str, field):
        model = self.env[field.comodel_name]
        record = model.search([('name', '=', value_str)], limit=1)
        if record:
            return record.id
        record = model.search([('display_name', '=', value_str)], limit=1)
        return record.id if record else False
