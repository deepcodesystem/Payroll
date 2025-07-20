# -- coding: utf-8 --
from odoo import api, fields, models


class OvertimeType(models.Model):
    """ Model to define different types of HR Overtime."""
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char('Name', help="Name of the overtime type.")
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')], string="Type",
                            help="Type of overtime, whether in cash or leave.")

    duration_type = fields.Selection([('hours', 'Hour'),
                                      ('days', 'Days')],
                                     string="Duration Type", default="hours",
                                     required=True,
                                     help="Duration type of the overtime, "
                                          "whether in hours or days.")
    leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type',
                                 domain="[('id', 'in', leave_compute_ids)]",
                                 help="Leave type associated with the overtime "
                                      "when the duration type is 'days'.")
    leave_compute_ids = fields.Many2many('hr.leave.type',
                                     compute="_get_leave_type",
                                     help="Computed field storing the available"
                                          "leave types associated with the "
                                          "overtime type.")
    rule_line_ids = fields.One2many('overtime.type.rule',
                                    'type_line_id',
                                    help="Rules associated with the overtime "
                                         "type.", string="Rules"
                                    )

    @api.onchange('duration_type')
    def _get_leave_type(self):
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute_ids = ids
