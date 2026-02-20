# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det


from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class hr_contract(models.Model):
    _inherit = 'hr.contract'
    _description='Add fields for moroccan payroll'

    indem_deplace = fields.Monetary(
        string='Indemnité de déplacement ',
        help="Elle est accordée aux salariés dont les conditions de travail nécessitent des déplacements de leur domicile vers un lieu de travail autre que le lieu habituel, situé en dehors du périmètre urbain et ce en remboursement des frais de nourriture, de logement et de transport qu’ils supportent."
    )
    indem_km = fields.Monetary(
        string="Indemnité kilométrique",
        help="Elle est accordée au salarié utilisant son propre véhicule pour l’exercice de ses fonctions professionnelles."
    )
    indem_transp = fields.Monetary(
        string="Indemnité de transport",
        help="Elle est accordée au salarié se rendant de son domicile au lieu habituel de son travail. 500 Dirhams par mois, dans le périmètre urbain des villes - 750 Dirhams par mois, lorsque le lieu de travail est situé en dehors du périmètre urbain de la ville."
    )
    prim_tournee = fields.Monetary(
        string="Prime de tournée",
        help="L’exonération est plafonnée à 1 500 Dirhams/mois."
    )
    indem_caisse = fields.Monetary(
        string="Indemnité de caisse",
        help="Le montant de l’indemnité admis en exonération ne doit pas dépasser 190 Dirhams par mois."
    )
    indem_rep = fields.Monetary(
        string="Indemnité de représentation",
        help="L’exonération est plafonnée à 10% du salaire de base."
    )
    prim_outil = fields.Monetary(
        string="Prime d’outillage",
        help="L’exonération est plafonnée à 100 Dirhams par mois."
    )
    prim_salis = fields.Monetary(
        string="Prime de salissure ",
        help="L’exonération est plafonnée à 210 Dirhams par mois."
    )
    prim_panier = fields.Monetary(
        string="Prime de panier",
        help="L’exonération est plafonnée à deux fois le SMIG horaire."
    )
    prim_panier = fields.Monetary(
        string="Prime de panier",
        help="L’exonération est plafonnée à deux fois le SMIG horaire."
    )
    grat_social = fields.Monetary(
        string="Gratifications sociales",
        help="L’indemnité est exonérée dans la limite de 2 500 Dirhams par an et couvre tous les événements confondus survenus au cours d’une même année."
    )
    indem_lice = fields.Monetary(
        string="Indemnité de licenciement",
        help="Cette indemnité est exonérée dans les limites fixées par le Code Général des Impôts"
    )
    prim_excep = fields.Monetary(
        string="Prime Exceptionnelle",
        help="Utiliser ce champ si la prime exceptionnelle doit être définit en permanence "
    )
    epargne_retraite = fields.Monetary(
        string="Epargne Retraite",
        help="Utiliser ce champ si l'éparge de retraite doit être définit en permanence "
    )
    epargne_retraite_ir = fields.Monetary(
        string="Epargne Retraite (IR)",
        help="Utiliser ce champ si l'éparge de retraite doit être définit en permanence "
    )
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