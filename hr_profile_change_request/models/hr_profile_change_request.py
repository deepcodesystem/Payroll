from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrProfileChangeRequest(models.Model):
    _name = 'hr.profile.change.request'
    _description = 'Demande de modification du profil RH'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Référence', required=True, copy=False, default='/', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=True,
        states=[('draft', [('readonly', False)])],
        domain="[('user_id', '=', uid)]")
    user_id = fields.Many2one('res.users', string='Utilisateur', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string='Société',
        default=lambda self: self.env.company, required=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('refused', 'Refusé'),
    ], string='État', default='draft', readonly=True, tracking=True)
    line_ids = fields.One2many('hr.profile.change.request.line', 'request_id', string='Modifications')
    hr_comment = fields.Text(string='Commentaire RH', readonly=True,
        states=[('pending', [('readonly', False)])])
    request_date = fields.Datetime(string='Date de demande', readonly=True)
    response_date = fields.Datetime(string='Date de réponse', readonly=True)
    can_approve = fields.Boolean(string='Peut approuver', compute='_compute_can_approve')

    @api.depends('state')
    def _compute_can_approve(self):
        is_hr = self.env.user.has_group('hr.group_hr_user')
        for rec in self:
            rec.can_approve = is_hr and rec.state == 'pending'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.profile.change.request') or '/'
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Veuillez ajouter au moins une modification.'))
            rec.write({
                'state': 'pending',
                'request_date': fields.Datetime.now(),
            })
            rec._notify_hr()

    def action_approve(self):
        for rec in self:
            if not rec.env.user.has_group('hr.group_hr_user'):
                raise UserError(_('Seul un responsable RH peut approuver cette demande.'))
            rec._apply_changes()
            rec.write({
                'state': 'approved',
                'response_date': fields.Datetime.now(),
            })
            rec._notify_employee()

    def action_refuse(self):
        for rec in self:
            if not rec.env.user.has_group('hr.group_hr_user'):
                raise UserError(_('Seul un responsable RH peut refuser cette demande.'))
            if not rec.hr_comment:
                raise UserError(_('Veuillez saisir un commentaire de refus.'))
            rec.write({
                'state': 'refused',
                'response_date': fields.Datetime.now(),
            })
            rec._notify_employee()

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state not in ('refused',):
                raise UserError(_('Seules les demandes refusées peuvent être remises en brouillon.'))
            rec.write({'state': 'draft', 'hr_comment': False, 'response_date': False})

    def _apply_changes(self):
        self.ensure_one()
        if not self.employee_id:
            return
        vals = {}
        for line in self.line_ids:
            field_name = line.field_name
            field = self.env['hr.employee']._fields.get(field_name)
            if not field:
                continue
            new_value = line._convert_to_field_type(line.new_value, field)
            vals[field_name] = new_value
        if vals:
            self.employee_id.sudo().write(vals)

    def _notify_hr(self):
        hr_group = self.env.ref('hr.group_hr_user', raise_if_not_found=False)
        if not hr_group:
            return
        hr_users = self.env['res.users'].search([
            ('groups_id', 'in', hr_group.ids),
            ('company_id', 'in', self.company_id.ids),
            ('active', '=', True),
        ])
        partner_ids = hr_users.mapped('partner_id').ids
        if partner_ids:
            self.message_post(
                body=_('Nouvelle demande de modification du profil de %s.', self.employee_id.name),
                subtype_xmlid='hr_profile_change_request.mt_profile_change_request',
                partner_ids=partner_ids,
            )

    def _notify_employee(self):
        employee_partner = self.employee_id.work_contact_id
        if not employee_partner:
            return
        if self.state == 'approved':
            body = _('Votre demande de modification du profil a été approuvée.')
        else:
            body = _('Votre demande de modification du profil a été refusée. Motif : %s', self.hr_comment or '')
        self.message_post(
            body=body,
            subtype_xmlid='hr_profile_change_request.mt_profile_change_request',
            partner_ids=[employee_partner.id],
        )
