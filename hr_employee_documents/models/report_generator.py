# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.misc import limited_field_access_token
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
            attachment = self.env['ir.attachment'].sudo().create({
                'name': filename,
                'datas': base64.b64encode(pdf_bytes),
                'type': 'binary',
                'mimetype': 'application/pdf',
            })

            # 6. Génération d'un token d'accès signé pour contourner les
            #    record rules Odoo sur ir.attachment (l'employé n'a pas
            #    d'accès ACL direct à hr.employee via base.group_user)
            token = limited_field_access_token(
                attachment.sudo(), 'raw'
            )

            # 7. Retour de l'action de téléchargement avec token
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true&access_token={token}',
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
        # Note: sudo() nécessaire pour outrepasser la règle core hr
        # "HR: Prevent non HR officers from accessing employee bank accounts"
        bank_account = employee.sudo().bank_account_id
        replacements = {
            # Employé
            '{{employee.name}}': safe_get(employee, 'name'),
            '{{employee.job_title}}': safe_get(employee, 'job_title'),
            '{{employee.department}}': safe_get(employee.department_id, 'name'),
            '{{employee.acc_number}}': safe_get(bank_account, 'acc_number'),
            '{{employee.agence}}': safe_get(bank_account, 'agence'),
            '{{employee.bank}}': safe_get(bank_account.bank_id, 'name'),
            '{{employee.email}}': safe_get(employee, 'work_email'),
            '{{employee.phone}}': safe_get(employee, 'mobile_phone'),
            '{{employee.private_street}}': safe_get(employee, 'private_street'),
            '{{employee.private_street2}}': safe_get(employee, 'private_street2'),
            '{{employee.private_zip}}': safe_get(employee, 'private_zip'),
            '{{employee.private_city}}': safe_get(employee, 'private_city'),
            '{{employee.id_number}}': safe_get(employee, 'identification_id'),
            '{{employee.hire_date}}': contract_date_str,
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

            # Salaire (depuis payslip ou contrat)
            '{{salary.base}}': self._get_salary_line(employee, 'BASE'),
            '{{salary.brut}}': self._get_salary_line(employee, 'GROSS'),
            '{{salary.amo}}': self._get_salary_line(employee, 'AMO'),
            '{{salary.cnss}}': self._get_salary_line(employee, 'CNSSE'),
            '{{salary.cimr}}': self._get_salary_line(employee, 'CIMRE'),
            '{{salary.amc}}': self._get_salary_line(employee, 'AMC_SAL'),
            '{{salary.igr}}': self._get_salary_line(employee, 'IR'),
            '{{salary.frais_pro}}': self._get_salary_line(employee, 'FRPRO'),
            '{{salary.net}}': self._get_salary_line(employee, 'NET'),
            '{{salary.note_frais}}': self._get_salary_line(employee, 'NOTE_FRAIS'),

            # Salaire net depuis le contrat
            '{{salary.net_contract}}': self._format_monetary(employee.contract_id.salary_net) if employee.contract_id and employee.contract_id.salary_net else '',
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
            return employee.birthday.strftime('%d-%m-%Y')
        return ''

    def _get_company_address(self, employee):
        if employee.company_id:
            c = employee.company_id
            parts = [p for p in [c.street, c.street2, c.zip, c.city] if p]
            return ' '.join(parts)
        return ''

    @staticmethod
    def _format_monetary(amount):
        """Formate un montant avec 2 décimales et séparateur de milliers"""
        try:
            return f"{float(amount):,.2f}".replace(',', ' ')
        except (ValueError, TypeError):
            return ''

    def _get_salary_line(self, employee, code):
        """Récupère une ligne de salaire depuis la dernière fiche de paie"""
        # sudo() pour permettre à l'employé d'accéder à ses propres bulletins
        payslip = self.env['hr.payslip'].sudo().search([
            ('employee_id', '=', employee.id),
            ('state', 'in', ['done', 'paid'])
        ], order='date_to desc', limit=1)

        if payslip:
            line = payslip.line_ids.filtered(lambda l: l.code == code)
            if line:
                return self._format_monetary(line[0].total)
        return ''
