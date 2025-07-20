# -- coding: utf-8 --
from odoo import fields, models


class OverTimeTypeRule(models.Model):
    """ Model to define rules associated with HR Overtime Types."""
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type',
                                   string='Over Time Type',
                                   help="Reference to the HR Overtime Type "
                                        "associated with this rule.")
    name = fields.Char('Name', required=True, help="Name of the overtime "
                                                   "rule.")
    from_hrs = fields.Float('From', required=True,
                            help="Start hour threshold for the overtime rule.")
    to_hrs = fields.Float('To', required=True,
                          help="End hour threshold for the overtime rule.")
    hrs_amount = fields.Float('Rate', required=True,
                              help="Rate of pay for the overtime rule.")
