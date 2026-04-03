# -*- coding: utf-8 -*-
import base64
import logging
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

SITUATION_RANG = {
    '  ': 0, 'SO': 1, 'DE': 2, 'IT': 3,
    'IL': 4, 'AT': 5, 'CS': 6, 'MS': 7, 'MP': 8,
}

SITUATION_LABELS = [
    ('', 'Normale (travail effectif)'),
    ('SO', 'SO - Sortant'),
    ('DE', 'DE - Décédé'),
    ('IT', 'IT - Maternité'),
    ('IL', 'IL - Maladie'),
    ('AT', 'AT - Accident de Travail'),
    ('CS', 'CS - Congé Sans Salaire'),
    ('MS', 'MS - Maintenu Sans Salaire'),
    ('MP', 'MP - Maladie Professionnelle'),
]


class CnssDeclaration(models.Model):
    _name = 'cnss.declaration'
    _description = 'Déclaration CNSS BDS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'periode desc, id desc'
    _rec_name = 'name'

    # ─── Identification ───────────────────────────────────────────────────
    name = fields.Char(
        string='Référence', readonly=True, copy=False,
        default='/', tracking=True,
    )
    affiliate_id = fields.Many2one(
        'cnss.affiliate', string='Affilié CNSS', required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', related='affiliate_id.company_id', store=True,
    )
    type_declaration = fields.Selection([
        ('principale', 'Principale'),
        ('complementaire', 'Complémentaire'),
    ], string='Type de Déclaration', required=True,
        default='principale', tracking=True,
    )
    num_complementaire = fields.Integer(
        string='N° Séquence Complémentaire', default=1,
        help='Numéro de séquence pour les déclarations complémentaires (1 à 9)',
    )
    declaration_principale_id = fields.Many2one(
        'cnss.declaration', string='Déclaration Principale liée',
        domain="[('type_declaration','=','principale')]",
    )

    # ─── Période ──────────────────────────────────────────────────────────
    periode_annee = fields.Integer(
        string='Année', required=True,
        default=lambda self: date.today().year,
    )
    periode_mois = fields.Selection([
        ('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'),
        ('04', 'Avril'), ('05', 'Mai'), ('06', 'Juin'),
        ('07', 'Juillet'), ('08', 'Août'), ('09', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True,
        default=lambda self: str(date.today().month).zfill(2),
    )
    periode = fields.Char(
        string='Période (AAAAMM)', compute='_compute_periode',
        store=True, readonly=True,
    )
    date_emission = fields.Date(
        string='Date d\'Émission', required=True,
        default=fields.Date.today,
    )
    date_exigibilite = fields.Date(
        string='Date d\'Exigibilité', required=True,
    )

    # ─── Référence structurée préétabli ───────────────────────────────────
    identif_transfert = fields.Char(
        string='Identifiant Transfert (préétabli)', size=14,
        help='Copier la valeur N_Identif_Transfert du fichier préétabli CNSS (A00)',
    )

    # ─── État ─────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('generated', 'Fichier Généré'),
        ('sent', 'Déposée CNSS'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    # ─── Lignes ───────────────────────────────────────────────────────────
    line_ids = fields.One2many(
        'cnss.declaration.line', 'declaration_id',
        string='Lignes Assurés (Existants)',
    )
    entrant_ids = fields.One2many(
        'cnss.entrant', 'declaration_id',
        string='Assurés Entrants',
    )

    # ─── Fichier généré ───────────────────────────────────────────────────
    bds_file = fields.Binary(string='Fichier BDS', readonly=True, attachment=True)
    bds_filename = fields.Char(string='Nom du fichier BDS', readonly=True)

    # ─── Totaux calculés ──────────────────────────────────────────────────
    total_salaries = fields.Integer(
        string='Total Salariés', compute='_compute_totaux', store=True,
    )
    total_salaries_existants = fields.Integer(
        string='Salariés Existants', compute='_compute_totaux', store=True,
    )
    total_salaries_entrants = fields.Integer(
        string='Salariés Entrants', compute='_compute_totaux', store=True,
    )
    total_jours = fields.Integer(
        string='Total Jours', compute='_compute_totaux', store=True,
    )
    total_sal_reel = fields.Float(
        string='Total Salaires Réels (centimes)', compute='_compute_totaux', store=True,
    )
    total_sal_plaf = fields.Float(
        string='Total Salaires Plafonnés (centimes)', compute='_compute_totaux', store=True,
    )
    total_af_a_payer = fields.Float(
        string='Total AF à Payer (centimes)', compute='_compute_totaux', store=True,
    )
    total_af_a_reverser = fields.Float(
        string='Total AF à Reverser (centimes)', compute='_compute_totaux', store=True,
    )

    note = fields.Text(string='Notes')

    # ─────────────────────────────────────────────────────────────────────
    # COMPUTES
    # ─────────────────────────────────────────────────────────────────────
    @api.depends('periode_annee', 'periode_mois')
    def _compute_periode(self):
        for rec in self:
            rec.periode = f"{rec.periode_annee}{rec.periode_mois}"

    @api.depends('line_ids', 'entrant_ids',
                 'line_ids.jours', 'line_ids.sal_reel', 'line_ids.sal_plaf',
                 'entrant_ids.jours', 'entrant_ids.sal_reel', 'entrant_ids.sal_plaf')
    def _compute_totaux(self):
        for rec in self:
            existants = rec.line_ids
            entrants = rec.entrant_ids
            rec.total_salaries_existants = len(existants)
            rec.total_salaries_entrants = len(entrants)
            rec.total_salaries = len(existants) + len(entrants)
            rec.total_jours = (
                    sum(l.jours for l in existants) +
                    sum(e.jours for e in entrants)
            )
            rec.total_sal_reel = (
                    sum(l.sal_reel for l in existants) +
                    sum(e.sal_reel for e in entrants)
            )
            rec.total_sal_plaf = (
                    sum(l.sal_plaf for l in existants) +
                    sum(e.sal_plaf for e in entrants)
            )
            rec.total_af_a_payer = sum(l.af_a_payer for l in existants)
            rec.total_af_a_reverser = sum(l.af_a_reverser for l in existants)

    # ─────────────────────────────────────────────────────────────────────
    # ORM OVERRIDES
    # ─────────────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cnss.declaration') or '/'
        return super().create(vals_list)

    @api.onchange('affiliate_id')
    def _onchange_affiliate_id(self):
        if self.affiliate_id:
            self.date_exigibilite = self._default_date_exig()

    def _default_date_exig(self):
        """Date d'exigibilité = dernier jour du mois suivant la période."""
        today = date.today()
        if today.month == 12:
            exig = date(today.year + 1, 1, 31)
        else:
            import calendar
            last_day = calendar.monthrange(today.year, today.month + 1)[1]
            exig = date(today.year, today.month + 1, last_day)
        return exig

    # ─────────────────────────────────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────────────────────────────────
    def action_confirm(self):
        for rec in self:
            rec._validate_declaration()
            rec.state = 'confirmed'
        return True

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_generate_bds(self):
        """Point d'entrée principal : génère et attache le fichier BDS."""
        self.ensure_one()
        self._validate_declaration()
        content = self._build_bds_content()
        # Encoder en latin-1 (ASCII étendu) pour compatibilité CNSS
        encoded = base64.b64encode(content.encode('latin-1', errors='replace'))
        filename = self._compute_filename()
        self.write({
            'bds_file': encoded,
            'bds_filename': filename,
            'state': 'generated',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cnss.declaration',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_mark_sent(self):
        self.ensure_one()
        self.state = 'sent'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_import_payslips(self):
        """Ouvre le wizard d'import des bulletins de paie."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Importer les Bulletins de Paie',
            'res_model': 'cnss.import.payslip.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_declaration_id': self.id},
        }

    def action_import_affebds(self):
        """Ouvre le wizard d'import du fichier préétabli AFFEBDS."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Fichier Préétabli AFFEBDS',
            'res_model': 'cnss.import.affebds.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_declaration_id': self.id},
        }

    # ─────────────────────────────────────────────────────────────────────
    # FILENAME
    # ─────────────────────────────────────────────────────────────────────
    def _compute_filename(self):
        """
        Principale : DS_NNNNNNN_MMAAAA.txt
        Complémentaire : DSC[N]_NNNNNNN_MMAAAA.txt
        """
        aff = self.affiliate_id.num_affilie.zfill(7)
        periode = f"{self.periode_mois}{self.periode_annee}"
        if self.type_declaration == 'principale':
            return f"DS_{aff}_{periode}.txt"
        else:
            n = self.num_complementaire or 1
            return f"DSC{n}_{aff}_{periode}.txt"

    # ─────────────────────────────────────────────────────────────────────
    # VALIDATION
    # ─────────────────────────────────────────────────────────────────────
    def _validate_declaration(self):
        self.ensure_one()
        errors = []

        aff = self.affiliate_id
        if not aff.num_affilie:
            errors.append("Le numéro d'affilié CNSS est obligatoire.")

        # Vérif lignes existantes
        for line in self.line_ids:
            sit = (line.situation or '').strip().upper()
            if sit in ('CS', 'MS'):
                if line.jours != 0 or line.sal_reel != 0:
                    errors.append(
                        f"Assuré {line.num_assure} : situation {sit} → jours et salaires doivent être nuls."
                    )
            elif sit == '':
                if line.jours <= 0 or line.sal_reel <= 0:
                    errors.append(
                        f"Assuré {line.num_assure} : situation normale → jours et salaire réel obligatoires."
                    )
            if line.jours > 26:
                errors.append(
                    f"Assuré {line.num_assure} : nombre de jours ({line.jours}) > 26."
                )
            if line.sal_plaf > line.sal_reel:
                errors.append(
                    f"Assuré {line.num_assure} : salaire plafonné > salaire réel."
                )
            if line.af_a_reverser > line.af_net_a_payer:
                errors.append(
                    f"Assuré {line.num_assure} : AF à reverser > AF net à payer."
                )

        # Vérif doublons num_assure
        nums = [l.num_assure for l in self.line_ids if l.num_assure]
        if len(nums) != len(set(nums)):
            errors.append("Des doublons existent dans les numéros d'immatriculation des assurés existants.")

        # Vérif entrants
        for ent in self.entrant_ids:
            if ent.jours > 26 or ent.jours <= 0:
                errors.append(
                    f"Entrant {ent.nom_prenom} : nombre de jours invalide ({ent.jours})."
                )
            if ent.sal_plaf > ent.sal_reel:
                errors.append(
                    f"Entrant {ent.nom_prenom} : salaire plafonné > salaire réel."
                )
            # Validation num imma si fourni
            num_assure = (ent.num_assure or '').strip()
            if num_assure and num_assure not in ('000000000', '999999999'):
                if not self._validate_num_imma(num_assure):
                    errors.append(
                        f"Entrant {ent.nom_prenom} : numéro d'immatriculation '{num_assure}' invalide."
                    )

        if errors:
            raise ValidationError("\n".join(errors))

    @staticmethod
    def _validate_num_imma(num):
        """
        Validation numéro immatriculation CNSS (9 chiffres).
        (C2+C4+C6+C8)*2 + C3+C5+C7 → unités → si 0 alors C9=0 sinon 10-unités = C9
        Premier chiffre doit être 1. '100000000' rejeté.
        """
        if not num or len(num) != 9 or not num.isdigit():
            return False
        if num[0] != '1':
            return False
        if num == '100000000':
            return False
        c = [int(x) for x in num]
        total = (c[1] + c[3] + c[5] + c[7]) * 2 + c[2] + c[4] + c[6]
        unite = total % 10
        cle = 0 if unite == 0 else (10 - unite)
        return cle == c[8]

    # ─────────────────────────────────────────────────────────────────────
    # BDS CONTENT BUILDER
    # ─────────────────────────────────────────────────────────────────────
    def _build_bds_content(self):
        """Assemble l'ensemble des enregistrements du fichier BDS."""
        self.ensure_one()
        is_compl = self.type_declaration == 'complementaire'
        prefix_b = 'E' if is_compl else 'B'
        lines = []

        # Enr 1 : B00 / E00
        lines.append(self._build_record_00(prefix_b))
        # Enr 2 : B01 / E01
        lines.append(self._build_record_01(prefix_b))

        if is_compl:
            # TD Complémentaire : une seule ligne E02 vide + E03 vide
            lines.append(self._build_record_E02())
            lines.append(self._build_record_E03())
            # Entrants E04
            entrants = self.entrant_ids.sorted(key=lambda e: e.num_assure or '0')
            for ent in entrants:
                lines.append(self._build_record_E04(ent))
            # E05 récap entrants
            lines.append(self._build_record_E05(entrants))
            # E06 récap global
            lines.append(self._build_record_E06(entrants))
        else:
            # TD Principale
            existants = self.line_ids.sorted(key=lambda l: int(l.num_assure or '0'))
            for line in existants:
                lines.append(self._build_record_B02(line))
            lines.append(self._build_record_B03(existants))

            entrants = self.entrant_ids.sorted(key=lambda e: e.num_assure or '0')
            if entrants:
                for ent in entrants:
                    lines.append(self._build_record_B04(ent))
            else:
                lines.append(self._build_record_B04_empty())
            lines.append(self._build_record_B05(entrants))
            lines.append(self._build_record_B06(existants, entrants))

        # Chaque ligne = 260 caractères + LF (ASCII 10)
        content = '\n'.join(lines) + '\n'
        # Vérification longueurs
        for i, line in enumerate(lines, 1):
            if len(line) != 260:
                _logger.warning(
                    "Ligne %d longueur incorrecte: %d au lieu de 260 → '%s'",
                    i, len(line), line[:30]
                )
        return content

    # ─── Helpers de formatage ─────────────────────────────────────────────
    @staticmethod
    def _pad_n(val, length):
        """Champ numérique : rempli à gauche avec des zéros."""
        return str(int(val or 0))[-length:].zfill(length)

    @staticmethod
    def _pad_an(val, length):
        """Champ alphanumérique : tronqué/complété avec des espaces à droite."""
        s = str(val or '')
        # Garder uniquement les caractères ASCII acceptés par la CNSS
        s = ''.join(c for c in s.upper() if c.isascii() and (c.isalnum() or c == ' ' or c == '\t'))
        return s[:length].ljust(length, ' ')

    def _get_aff_info(self):
        aff = self.affiliate_id
        return {
            'num': aff.num_affilie.zfill(7),
            'periode': self.periode.zfill(6),
            'raison': aff.raison_sociale or '',
            'activite': aff.activite or '',
            'adresse': aff.adresse or '',
            'ville': aff.ville or '',
            'code_postal': aff.code_postal or '',
            'code_agence': aff.code_agence or '',
            'date_emission': (self.date_emission or date.today()).strftime('%Y%m%d'),
            'date_exig': (self.date_exigibilite or date.today()).strftime('%Y%m%d'),
        }

    # ─── Enregistrement B00 / E00 ─────────────────────────────────────────
    def _build_record_00(self, prefix):
        pn = self._pad_n
        pan = self._pad_an
        identif = self.identif_transfert or '00000000000000'
        if prefix == 'B':
            cat = 'B0'
        else:
            n = self.num_complementaire or 1
            cat = f"E{n}"
        rec = (
                pan(f"{prefix}00", 3) +
                pn(identif, 14) +
                pan(cat, 2) +
                pan('', 241)
        )
        return rec

    # ─── Enregistrement B01 / E01 ─────────────────────────────────────────
    def _build_record_01(self, prefix):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        rec = (
                pan(f"{prefix}01", 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pan(a['raison'], 40) +
                pan(a['activite'], 40) +
                pan(a['adresse'], 120) +
                pan(a['ville'], 20) +
                pan(a['code_postal'], 6) +
                pn(a['code_agence'], 2) +
                pn(a['date_emission'], 8) +
                pn(a['date_exig'], 8)
        )
        return rec

    # ─── Enregistrement B02 (détail assuré existant) ──────────────────────
    def _build_record_B02(self, line):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        sit = (line.situation or '').strip().upper().ljust(2)
        rang = SITUATION_RANG.get(sit.rstrip() or '  ', 0)

        ctr = (
                int(line.num_assure or 0) +
                int(line.af_a_reverser or 0) +
                int(line.jours or 0) +
                int(line.sal_reel or 0) +
                int(line.sal_plaf or 0) +
                rang
        )
        rec = (
                pan('B02', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(line.num_assure, 9) +
                pan(line.nom_prenom, 60) +
                pn(line.enfants, 2) +
                pn(line.af_a_payer, 6) +
                pn(line.af_a_deduire, 6) +
                pn(line.af_net_a_payer, 6) +
                pn(line.af_a_reverser, 6) +
                pn(line.jours, 2) +
                pn(line.sal_reel, 13) +
                pn(line.sal_plaf, 9) +
                sit +
                pn(ctr, 19) +
                pan('', 104)
        )
        return rec

    # ─── Enregistrement B03 (récap existants) ────────────────────────────
    def _build_record_B03(self, existants):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()

        nb = len(existants)
        t_enf = sum(int(l.enfants or 0) for l in existants)
        t_af_payer = sum(int(l.af_a_payer or 0) for l in existants)
        t_af_deduire = sum(int(l.af_a_deduire or 0) for l in existants)
        t_af_net = sum(int(l.af_net_a_payer or 0) for l in existants)
        t_imma = sum(int(l.num_assure or 0) for l in existants)
        t_af_rev = sum(int(l.af_a_reverser or 0) for l in existants)
        t_jours = sum(int(l.jours or 0) for l in existants)
        t_reel = sum(int(l.sal_reel or 0) for l in existants)
        t_plaf = sum(int(l.sal_plaf or 0) for l in existants)
        t_ctr = self._compute_ctr_existants(existants)

        rec = (
                pan('B03', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(nb, 6) +
                pn(t_enf, 6) +
                pn(t_af_payer, 12) +
                pn(t_af_deduire, 12) +
                pn(t_af_net, 12) +
                pn(t_imma, 15) +
                pn(t_af_rev, 12) +
                pn(t_jours, 6) +
                pn(t_reel, 15) +
                pn(t_plaf, 13) +
                pn(t_ctr, 19) +
                pan('', 116)
        )
        return rec

    def _compute_ctr_existants(self, existants):
        total = 0
        for l in existants:
            sit = (l.situation or '').strip().upper().ljust(2)
            rang = SITUATION_RANG.get(sit.rstrip() or '  ', 0)
            total += (
                    int(l.num_assure or 0) +
                    int(l.af_a_reverser or 0) +
                    int(l.jours or 0) +
                    int(l.sal_reel or 0) +
                    int(l.sal_plaf or 0) +
                    rang
            )
        return total

    # ─── Enregistrement B04 (détail entrant) ─────────────────────────────
    def _build_record_B04(self, ent):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        num_assure = (ent.num_assure or '').strip() or '000000000'
        ctr = (
                int(num_assure) +
                int(ent.jours or 0) +
                int(ent.sal_reel or 0) +
                int(ent.sal_plaf or 0)
        )
        rec = (
                pan('B04', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(num_assure, 9) +
                pan(ent.nom_prenom, 60) +
                pan(ent.num_cin, 8) +
                pn(ent.jours, 2) +
                pn(ent.sal_reel, 13) +
                pn(ent.sal_plaf, 9) +
                pn(ctr, 19) +
                pan('', 124)
        )
        return rec

    def _build_record_B04_empty(self):
        """B04 vide quand pas d'entrants (9 espaces dans num_assure)."""
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        rec = (
                pan('B04', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pan('', 9) +  # 9 espaces vides
                pan('', 60) +
                pan('', 8) +
                pn(0, 2) +
                pn(0, 13) +
                pn(0, 9) +
                pn(0, 19) +
                pan('', 124)
        )
        return rec

    # ─── Enregistrement B05 (récap entrants) ─────────────────────────────
    def _build_record_B05(self, entrants):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        nb = len(entrants)
        t_imma = sum(int((e.num_assure or '0').strip() or '0') for e in entrants)
        t_jours = sum(int(e.jours or 0) for e in entrants)
        t_reel = sum(int(e.sal_reel or 0) for e in entrants)
        t_plaf = sum(int(e.sal_plaf or 0) for e in entrants)
        t_ctr = self._compute_ctr_entrants(entrants)
        rec = (
                pan('B05', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(nb, 6) +
                pn(t_imma, 15) +
                pn(t_jours, 6) +
                pn(t_reel, 15) +
                pn(t_plaf, 13) +
                pn(t_ctr, 19) +
                pan('', 170)
        )
        return rec

    def _compute_ctr_entrants(self, entrants):
        total = 0
        for e in entrants:
            num = int((e.num_assure or '0').strip() or '0')
            total += num + int(e.jours or 0) + int(e.sal_reel or 0) + int(e.sal_plaf or 0)
        return total

    # ─── Enregistrement B06 (récap global) ───────────────────────────────
    def _build_record_B06(self, existants, entrants):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        nb = len(existants) + len(entrants)
        t_imma = (
                sum(int(l.num_assure or 0) for l in existants) +
                sum(int((e.num_assure or '0').strip() or '0') for e in entrants)
        )
        t_jours = (
                sum(int(l.jours or 0) for l in existants) +
                sum(int(e.jours or 0) for e in entrants)
        )
        t_reel = (
                sum(int(l.sal_reel or 0) for l in existants) +
                sum(int(e.sal_reel or 0) for e in entrants)
        )
        t_plaf = (
                sum(int(l.sal_plaf or 0) for l in existants) +
                sum(int(e.sal_plaf or 0) for e in entrants)
        )
        t_ctr = (
                self._compute_ctr_existants(existants) +
                self._compute_ctr_entrants(entrants)
        )
        rec = (
                pan('B06', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(nb, 6) +
                pn(t_imma, 15) +
                pn(t_jours, 6) +
                pn(t_reel, 15) +
                pn(t_plaf, 13) +
                pn(t_ctr, 19) +
                pan('', 170)
        )
        return rec

    # ─── Enregistrements complémentaires E02/E03/E04/E05/E06 ─────────────
    def _build_record_E02(self):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        rec = (
                pan('E02', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pan('', 9) +  # espaces
                pan('', 60) +
                pn(0, 2) +
                pn(0, 6) +
                pn(0, 6) +
                pn(0, 6) +
                pn(0, 6) +
                pn(0, 2) +
                pn(0, 13) +
                pn(0, 9) +
                pan('  ', 2) +
                pn(0, 19) +
                pan('', 104)
        )
        return rec

    def _build_record_E03(self):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        rec = (
                pan('E03', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(0, 6) +
                pn(0, 6) +
                pn(0, 12) +
                pn(0, 12) +
                pn(0, 12) +
                pn(0, 15) +
                pn(0, 12) +
                pn(0, 6) +
                pn(0, 15) +
                pn(0, 13) +
                pn(0, 19) +
                pan('', 116)
        )
        return rec

    def _build_record_E04(self, ent):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        num_assure = (ent.num_assure or '').strip() or '000000000'
        ctr = (
                int(num_assure) +
                int(ent.jours or 0) +
                int(ent.sal_reel or 0) +
                int(ent.sal_plaf or 0)
        )
        rec = (
                pan('E04', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(num_assure, 9) +
                pan(ent.nom_prenom, 60) +
                pan(ent.num_cin, 8) +
                pn(ent.jours, 2) +
                pn(ent.sal_reel, 13) +
                pn(ent.sal_plaf, 9) +
                pn(ctr, 19) +
                pan('', 124)
        )
        return rec

    def _build_record_E05(self, entrants):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        nb = len(entrants)
        t_imma = sum(int((e.num_assure or '0').strip() or '0') for e in entrants)
        t_jours = sum(int(e.jours or 0) for e in entrants)
        t_reel = sum(int(e.sal_reel or 0) for e in entrants)
        t_plaf = sum(int(e.sal_plaf or 0) for e in entrants)
        t_ctr = self._compute_ctr_entrants(entrants)
        rec = (
                pan('E05', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(nb, 6) +
                pn(t_imma, 15) +
                pn(t_jours, 6) +
                pn(t_reel, 15) +
                pn(t_plaf, 13) +
                pn(t_ctr, 19) +
                pan('', 170)
        )
        return rec

    def _build_record_E06(self, entrants):
        pn = self._pad_n
        pan = self._pad_an
        a = self._get_aff_info()
        nb = len(entrants)
        t_imma = sum(int((e.num_assure or '0').strip() or '0') for e in entrants)
        t_jours = sum(int(e.jours or 0) for e in entrants)
        t_reel = sum(int(e.sal_reel or 0) for e in entrants)
        t_plaf = sum(int(e.sal_plaf or 0) for e in entrants)
        t_ctr = self._compute_ctr_entrants(entrants)
        rec = (
                pan('E06', 3) +
                pn(a['num'], 7) +
                pn(a['periode'], 6) +
                pn(nb, 6) +
                pn(t_imma, 15) +
                pn(t_jours, 6) +
                pn(t_reel, 15) +
                pn(t_plaf, 13) +
                pn(t_ctr, 19) +
                pan('', 170)
        )
        return rec
