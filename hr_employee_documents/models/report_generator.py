# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import base64


class ReportTemplateGenerator(models.TransientModel):
    """Helper to generate reports from templates using Odoo Qweb"""
    _name = 'hr.report.template.generator'
    _description = 'Report Template Generator'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.context.get('default_employee_id')
    )
    template_id = fields.Many2one(
        'hr.employee.report.template',
        string='Template',
        required=True
    )

    def generate_report(self):
        """Generate and download PDF report using Odoo's internal engine"""
        self.ensure_one()

        # 1. Récupération du contenu fusionné avec les données employé
        content = self._get_filled_content()

        # 2. Construction du HTML complet (en format texte/String)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.template_id.name}</title>
    <style>
        /* Configuration de la page pour éviter les débordements */
        @page {{
            size: A4;
        }}
        html, body {{
            margin: 0;
            padding: 0 80px;
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background-color: white;
        }}
        .page {{
            /* On retire le page-break-after: always qui causait la page blanche */
            width: 100%;
            box-sizing: border-box;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        table, th, td {{
            border: 1px solid #333;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
        h1 {{ font-size: 24px; margin-bottom: 20px; text-align: center; }}
        h2 {{ font-size: 18px; margin-bottom: 12px; }}
        p {{ margin: 8px 0; }}
        .underline {{ text-decoration: underline; }}

        /* Optionnel : Empêcher les tableaux de se couper en deux */
        tr, table {{
            page-break-inside: avoid;
        }}
    </style>
</head>
<body>
    <div class="page">
        {content}
    </div>
</body>
</html>
"""

        try:
            # 3. Conversion en PDF via le moteur d'Odoo
            # On envoie une liste contenant la chaîne HTML (String)
            pdf_bytes = self.env['ir.actions.report']._run_wkhtmltopdf([html_content])

            if not pdf_bytes:
                raise UserError(_("Le moteur PDF a renvoyé un fichier vide."))

            # 4. Préparation du nom de fichier
            emp_name = str(self.employee_id.name).replace(' ', '_').replace('/', '-').replace('\\', '-')
            template_code = str(self.template_id.code or 'DOC').replace(' ', '_')
            filename = f"{template_code}_{emp_name}.pdf"

            # 5. Création de l'attachement
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(pdf_bytes),
                'type': 'binary',
                'mimetype': 'application/pdf',
            })

            # 6. Retour de l'action de téléchargement
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except Exception as e:
            raise UserError(_('Erreur lors de la génération du document : %s') % str(e))

    def _get_filled_content(self):
        """Remplit le template avec toutes les variables de l'employé"""
        content = self.template_id.template_content or ''
        employee = self.employee_id

        if not content:
            return '<p>Le contenu du template est vide.</p>'

        # Helper pour extraire les données proprement
        def safe_get(obj, attr, default=''):
            try:
                if not obj: return default
                value = getattr(obj, attr, None)
                if value is None or value is False: return default
                if hasattr(value, 'name'): return str(value.name)
                return str(value)
            except:
                return default

        # Préparation des dates
        hire_date_str = ''
        if employee.create_date:
            hire_date_str = employee.create_date.strftime('%d/%m/%Y')

        contract_date_str = ''
        if employee.contract_id and employee.contract_id.date_start:
            contract_date_str = employee.contract_id.date_start.strftime('%d/%m/%Y')

        # Dictionnaire des remplacements (vos anciens champs)
        replacements = {
            # Employé
            '{{employee.name}}': safe_get(employee, 'name'),
            '{{employee.job_title}}': safe_get(employee, 'job_title'),
            '{{employee.department}}': safe_get(employee.department_id, 'name'),
            '{{employee.acc_number}}': safe_get(employee.bank_account_id, 'acc_number'),
            '{{employee.agence}}': safe_get(employee.bank_account_id, 'agence'),
            '{{employee.bank}}': safe_get(employee.bank_account_id.bank_id, 'name'),
            '{{employee.email}}': safe_get(employee, 'work_email'),
            '{{employee.phone}}': safe_get(employee, 'mobile_phone'),
            '{{employee.private_street}}': safe_get(employee, 'private_street'),
            '{{employee.private_street2}}': safe_get(employee, 'private_street2'),
            '{{employee.private_zip}}': safe_get(employee, 'private_zip'),
            '{{employee.private_city}}': safe_get(employee, 'private_city'),
            '{{employee.id_number}}': safe_get(employee, 'identification_id'),
            '{{employee.hire_date}}': hire_date_str,
            '{{employee.ssnid}}': safe_get(employee, 'ssnid'),
            '{{gender}}': self._get_gender_display(employee),
            '{{employee.birth_date}}': self._get_birth_date(employee),

            # Dates
            '{{today_date}}': datetime.now().strftime('%d/%m/%Y'),
            '{{today_date_long}}': datetime.now().strftime('%d %B %Y'),

            # Société
            '{{company_name}}': safe_get(employee.company_id, 'name'),
            '{{company_address}}': self._get_company_address(employee),
            '{{company_city}}': safe_get(employee.company_id, 'city'),

            # Contrat
            '{{contract_date}}': contract_date_str,
        }

        # Application des remplacements
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value or ''))

        return content

    # --- Fonctions Helpers ---
    def _get_gender_display(self, employee):
        if hasattr(employee, 'gender'):
            return 'Mr' if employee.gender == 'male' else 'Mme'
        return 'Mr'

    def _get_birth_date(self, employee):
        if hasattr(employee, 'birthday') and employee.birthday:
            return employee.birthday.strftime('%d/%m/%Y')
        return ''

    def _get_company_address(self, employee):
        if employee.company_id:
            c = employee.company_id
            parts = [p for p in [c.street, c.street2, c.zip, c.city] if p]
            return ' '.join(parts)
        return ''
