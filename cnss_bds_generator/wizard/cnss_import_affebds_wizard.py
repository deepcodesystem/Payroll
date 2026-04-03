# -*- coding: utf-8 -*-
import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CnssImportAffebdsWizard(models.TransientModel):
    _name = 'cnss.import.affebds.wizard'
    _description = 'Import fichier préétabli AFFEBDS Damancom'

    declaration_id = fields.Many2one(
        'cnss.declaration', string='Déclaration CNSS', required=True,
        readonly=True,
    )
    affebds_file = fields.Binary(
        string='Fichier AFFEBDS', required=True,
        help='Fichier préétabli téléchargé depuis le portail Damancom (AFFEBDS_*.txt)',
    )
    affebds_filename = fields.Char(string='Nom du fichier')
    replace_existing = fields.Boolean(
        string='Remplacer les lignes existantes', default=True,
        help='Si coché, supprime les lignes existantes avant import',
    )
    update_affiliate = fields.Boolean(
        string='Mettre à jour les infos affilié', default=True,
        help='Met à jour raison sociale, adresse depuis le fichier',
    )

    # Résultats du parsing (aperçu)
    state = fields.Selection([
        ('upload', 'Upload'),
        ('preview', 'Aperçu'),
    ], default='upload')

    # Infos affilié parsées
    parsed_num_affilie = fields.Char(string='N° Affilié', readonly=True)
    parsed_periode = fields.Char(string='Période', readonly=True)
    parsed_raison_sociale = fields.Char(string='Raison Sociale', readonly=True)
    parsed_adresse = fields.Char(string='Adresse', readonly=True)
    parsed_ville = fields.Char(string='Ville', readonly=True)
    parsed_code_postal = fields.Char(string='Code Postal', readonly=True)
    parsed_code_agence = fields.Char(string='Code Agence', readonly=True)
    parsed_date_emission = fields.Date(string='Date Émission', readonly=True)
    parsed_date_exigibilite = fields.Date(string='Date Exigibilité', readonly=True)
    parsed_identif_transfert = fields.Char(string='Identifiant Transfert', readonly=True)
    parsed_total_assures = fields.Integer(string='Nb Assurés', readonly=True)

    preview_line_ids = fields.One2many(
        'cnss.import.affebds.line', 'wizard_id',
        string='Lignes prévisualisées',
    )

    def action_parse_file(self):
        """Parse le fichier AFFEBDS et affiche l'aperçu."""
        self.ensure_one()
        if not self.affebds_file:
            raise UserError("Veuillez sélectionner un fichier AFFEBDS.")

        try:
            content = base64.b64decode(self.affebds_file).decode('latin-1')
        except Exception as e:
            raise UserError(f"Erreur de lecture du fichier : {e}")

        lines = content.strip().split('\n')
        if len(lines) < 3:
            raise UserError("Le fichier semble incomplet (moins de 3 lignes).")

        # Parser le fichier
        parsed = self._parse_affebds(lines)

        # Mise à jour des champs d'aperçu
        self.write({
            'state': 'preview',
            'parsed_num_affilie': parsed['num_affilie'],
            'parsed_periode': parsed['periode'],
            'parsed_raison_sociale': parsed['raison_sociale'],
            'parsed_adresse': parsed['adresse'],
            'parsed_ville': parsed['ville'],
            'parsed_code_postal': parsed['code_postal'],
            'parsed_code_agence': parsed['code_agence'],
            'parsed_date_emission': parsed['date_emission'],
            'parsed_date_exigibilite': parsed['date_exigibilite'],
            'parsed_identif_transfert': parsed['identif_transfert'],
            'parsed_total_assures': parsed['total_assures'],
        })

        # Supprimer anciennes lignes preview
        self.preview_line_ids.unlink()

        # Créer lignes preview
        for assure in parsed['assures']:
            self.env['cnss.import.affebds.line'].create({
                'wizard_id': self.id,
                'num_assure': assure['num_assure'],
                'nom': assure['nom'],
                'prenom': assure['prenom'],
                'nom_prenom': f"{assure['nom']} {assure['prenom']}".strip(),
                'enfants': assure.get('enfants', 0),
                'af_a_payer': assure.get('af_a_payer', 0),
                'af_a_deduire': assure.get('af_a_deduire', 0),
                'a_importer': True,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _parse_affebds(self, lines):
        """
        Parse un fichier AFFEBDS selon le format Damancom.

        Format des enregistrements :
        - A00 : Identifiant transfert (pos 3-16 = 14 chars)
        - A01 : Infos affilié
        - A02 : Détail assuré (plusieurs lignes)
        - A03 : Récapitulatif
        """
        result = {
            'identif_transfert': '',
            'num_affilie': '',
            'periode': '',
            'raison_sociale': '',
            'adresse': '',
            'ville': '',
            'code_postal': '',
            'code_agence': '',
            'date_emission': None,
            'date_exigibilite': None,
            'total_assures': 0,
            'assures': [],
        }

        for line in lines:
            line = line.rstrip()
            if len(line) < 3:
                continue

            record_type = line[:3]

            if record_type == 'A00':
                # Identifiant transfert : position 3-16 (14 chars)
                result['identif_transfert'] = line[3:17].strip()

            elif record_type == 'A01':
                # A01 : Infos affilié
                # Position 3-9 (7 chars) : N° affilié
                # Position 10-15 (6 chars) : Période AAAAMM
                # Position 16-55 (40 chars) : Raison sociale
                # Position 56-175 (120 chars) : Adresse
                # Position 176-195 (20 chars) : Ville
                # Position 196-201 (6 chars) : Code postal (5 chiffres + espace ou 6 chars)
                # Position 202-203 (2 chars) : Code agence
                # Position 204-211 (8 chars) : Date émission AAAAMMJJ
                # Position 212-219 (8 chars) : Date exigibilité AAAAMMJJ
                result['num_affilie'] = line[3:10].strip()
                result['periode'] = line[10:16].strip()
                result['raison_sociale'] = line[16:56].strip()
                result['adresse'] = line[56:176].strip()
                result['ville'] = line[176:196].strip()
                result['code_postal'] = line[196:202].strip()
                result['code_agence'] = line[202:204].strip()

                date_em = line[204:212].strip()
                if len(date_em) == 8 and date_em.isdigit():
                    from datetime import date
                    try:
                        result['date_emission'] = date(
                            int(date_em[:4]), int(date_em[4:6]), int(date_em[6:8])
                        )
                    except ValueError:
                        pass

                date_ex = line[212:220].strip()
                if len(date_ex) == 8 and date_ex.isdigit():
                    from datetime import date
                    try:
                        result['date_exigibilite'] = date(
                            int(date_ex[:4]), int(date_ex[4:6]), int(date_ex[6:8])
                        )
                    except ValueError:
                        pass

            elif record_type == 'A02':
                # A02 : Détail assuré
                # Position 3-9 (7 chars) : N° affilié
                # Position 10-15 (6 chars) : Période
                # Position 16-24 (9 chars) : N° immatriculation CNSS
                # Position 25-54 (30 chars) : Nom
                # Position 55-84 (30 chars) : Prénom
                # Position 85-86 (2 chars) : Nb enfants (à vérifier)
                # Position 87-92 (6 chars) : AF à payer
                # Position 93-98 (6 chars) : AF à déduire
                num_assure = line[16:25].strip()
                nom = line[25:55].strip()
                prenom = line[55:85].strip()

                # Les positions des AF peuvent varier, parser avec prudence
                enfants = 0
                af_a_payer = 0
                af_a_deduire = 0

                # Chercher les valeurs numériques après le prénom
                reste = line[85:].strip()
                if reste and reste[:20].replace('0', '') == '':
                    # Ligne avec zéros = pas de données AF dans ce format
                    pass

                result['assures'].append({
                    'num_assure': num_assure,
                    'nom': nom,
                    'prenom': prenom,
                    'enfants': enfants,
                    'af_a_payer': af_a_payer,
                    'af_a_deduire': af_a_deduire,
                })

            elif record_type == 'A03':
                # A03 : Récapitulatif
                # Position 3-9 (7 chars) : N° affilié
                # Position 10-15 (6 chars) : Période
                # Position 16-21 (6 chars) : Nombre d'assurés
                nb_str = line[16:22].strip()
                if nb_str.isdigit():
                    result['total_assures'] = int(nb_str)

        # Si total_assures non trouvé, le calculer
        if result['total_assures'] == 0:
            result['total_assures'] = len(result['assures'])

        return result

    def action_import(self):
        """Importe les données parsées dans la déclaration."""
        self.ensure_one()
        if self.state != 'preview':
            raise UserError("Veuillez d'abord parser le fichier.")

        decl = self.declaration_id

        # Vérification de cohérence affilié/période
        aff = decl.affiliate_id
        if aff.num_affilie != self.parsed_num_affilie:
            raise ValidationError(
                f"Le numéro d'affilié du fichier ({self.parsed_num_affilie}) "
                f"ne correspond pas à celui de la déclaration ({aff.num_affilie})."
            )

        # Vérification période
        file_periode = self.parsed_periode  # Format AAAAMM
        decl_periode = decl.periode  # Format AAAAMM
        if file_periode and decl_periode and file_periode != decl_periode:
            raise ValidationError(
                f"La période du fichier ({file_periode}) ne correspond pas "
                f"à celle de la déclaration ({decl_periode})."
            )

        # Mise à jour infos affilié si demandé
        if self.update_affiliate and aff:
            update_vals = {}
            if self.parsed_raison_sociale:
                update_vals['raison_sociale'] = self.parsed_raison_sociale[:40]
            if self.parsed_adresse:
                update_vals['adresse'] = self.parsed_adresse[:120]
            if self.parsed_ville:
                update_vals['ville'] = self.parsed_ville[:20]
            if self.parsed_code_postal:
                update_vals['code_postal'] = self.parsed_code_postal[:6]
            if self.parsed_code_agence:
                update_vals['code_agence'] = self.parsed_code_agence[:2]
            if update_vals:
                aff.write(update_vals)

        # Mise à jour déclaration
        decl_update = {}
        if self.parsed_identif_transfert:
            decl_update['identif_transfert'] = self.parsed_identif_transfert
        if self.parsed_date_emission:
            decl_update['date_emission'] = self.parsed_date_emission
        if self.parsed_date_exigibilite:
            decl_update['date_exigibilite'] = self.parsed_date_exigibilite
        if decl_update:
            decl.write(decl_update)

        # Suppression des lignes existantes si demandé
        if self.replace_existing:
            decl.line_ids.unlink()

        # Import des lignes assurés
        lines_to_import = self.preview_line_ids.filtered(lambda l: l.a_importer)
        if not lines_to_import:
            raise UserError("Aucune ligne sélectionnée pour l'import.")

        # Recherche des employés correspondants par numéro CNSS
        emp_model = self.env['hr.employee']

        for line in lines_to_import:
            # Chercher l'employé par numéro CNSS
            employee = emp_model.search([
                ('ssnid', '=', line.num_assure),
                '|',
                ('company_id', '=', decl.company_id.id),
                ('company_id', '=', False),
            ], limit=1)

            self.env['cnss.declaration.line'].create({
                'declaration_id': decl.id,
                'employee_id': employee.id if employee else False,
                'num_assure': line.num_assure,
                'nom_prenom': line.nom_prenom,
                'enfants': line.enfants,
                'af_a_payer': line.af_a_payer,
                'af_a_deduire': line.af_a_deduire,
                'af_a_reverser': 0,
                'jours': 0,
                'sal_reel': 0,
                'sal_plaf': 0,
                'situation': '',
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cnss.declaration',
            'res_id': decl.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_back_upload(self):
        """Retour à l'étape upload."""
        self.write({
            'state': 'upload',
            'affebds_file': False,
            'affebds_filename': False,
        })
        self.preview_line_ids.unlink()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class CnssImportAffebdsLine(models.TransientModel):
    _name = 'cnss.import.affebds.line'
    _description = 'Ligne aperçu import AFFEBDS'

    wizard_id = fields.Many2one('cnss.import.affebds.wizard', ondelete='cascade')
    num_assure = fields.Char(string='N° Imma CNSS')
    nom = fields.Char(string='Nom')
    prenom = fields.Char(string='Prénom')
    nom_prenom = fields.Char(string='Nom & Prénom')
    enfants = fields.Integer(string='Enfants AF')
    af_a_payer = fields.Integer(string='AF à Payer (cts)')
    af_a_deduire = fields.Integer(string='AF à Déduire (cts)')
    a_importer = fields.Boolean(string='À Importer', default=True)

