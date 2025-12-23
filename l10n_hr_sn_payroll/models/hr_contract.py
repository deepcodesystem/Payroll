# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det
from email.policy import default

from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description='Add fields for moroccan payroll'

    indem_transp = fields.Monetary(
        string="Indemnité de transport",
        default="26000.0",
        help="Elle est due à tout salarié ne bénéficiant pas d'un transport assuré par l'entreprise.."
             "Le montant légal est de 26 000 F CFA par mois depuis juillet 2023. Tout montant versé au-delà de ce plafond légal (sauf justification de frais réels supérieurs) est généralement réintégré dans l'assiette imposable. "
    )
    indem_panier = fields.Monetary(
        string="Indemnité de panier",
        help="Le salarié doit être contraint de prendre son repas sur son lieu de travail (ex: travail de nuit, horaires décalés, ou travail continu sans pause suffisante pour rentrer). Elle est exonérée si son montant reste raisonnable par rapport au coût local d'un repas. Elle est limitée à un panier par jour de travail effectif remplissant les conditions"
    )
    indem_km = fields.Monetary(
        string="Indemnité Kilométrique",
        help="Indemnité versée au salarié utilisant son véhicule personnel pour des déplacements professionnels."
    )
    minima_categ_id = fields.Many2one(
        'min.categoriels',
        string='Catégorie de Minima',
        help="Sélectionner la catégorie de minima applicable au salarié (ex: 1ère A, 1ère B, etc.)"
    )
    minima_categ_amount = fields.Monetary(
        string="Montant Catégorie",
        compute='_compute_minima_categ_amount',
        store=False,
        help="Montant minimum selon la catégorie sélectionnée"
    )
    sursalaire_base = fields.Monetary(
        string="Sursalaire de Base",
        help="Montant supplémentaire au-delà du salaire minimum de la catégorie"
    )

    @api.depends('minima_categ_id')
    def _compute_minima_categ_amount(self):
        for record in self:
            if record.minima_categ_id:
                record.minima_categ_amount = record.minima_categ_id.amount
            else:
                record.minima_categ_amount = 0
    worked_age = fields.Char(
        string='Ancienneté',
        group='hr.group_hr_user',
        compute='_get_worked_age'
    )

    @api.depends("date_start")
    def _get_worked_age(self):
        for record in self:
            if record.date_start:
                date_start = record.date_start
                now = datetime.now()
                age = relativedelta(now, date_start)
            record.worked_age = f"{age.years} années {age.months} mois et {age.days} jours"