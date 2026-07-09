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

        if not content:
            return '<p>Le contenu du template est vide.</p>'

        # Lecture de toutes les données employé en une seule requête sudo()
        # pour contourner le fetch override de hr.employee qui restreint
        # les champs customs (dependants, cimr_id, etc.) via hr.employee.public
        emp = self.env['hr.employee'].sudo().browse(self.employee_id.id)
        emp_data = emp.read([
            'name', 'job_title', 'department_id', 'work_email', 'mobile_phone',
            'private_street', 'private_street2', 'private_zip', 'private_city',
            'identification_id', 'ssnid', 'gender', 'birthday', 'company_id',
            'contract_id', 'bank_account_id',
        ])
        if emp_data:
            emp_data = emp_data[0]
        else:
            emp_data = {}

        # Helper d'extraction sécurisée depuis un dict
        # Note: read() retourne les Many2one comme (id, name) tuples
        def _id(val):
            return val[0] if isinstance(val, (tuple, list)) else val

        def dget(d, key, default=''):
            val = d.get(key)
            if val is None or val is False:
                return default
            return str(val)

        # Données bancaires
        bank_account = emp.bank_account_id
        bank_name = bank_account.bank_id.name or '' if bank_account.bank_id else ''

        # Dates
        hire_date_str = ''
        if emp.create_date:
            hire_date_str = emp.create_date.strftime('%d/%m/%Y')

        contract_date_str = ''
        contract_id = _id(emp_data.get('contract_id'))
        if contract_id:
            contract = self.env['hr.contract'].sudo().browse(contract_id)
            if contract.date_start:
                contract_date_str = contract.date_start.strftime('%d/%m/%Y')

        # Société
        company_name = ''
        company_city = ''
        company_address = ''
        company_id = _id(emp_data.get('company_id'))
        if company_id:
            company = self.env['res.company'].sudo().browse(company_id)
            company_name = company.name or ''
            company_city = company.city or ''
            parts = [p for p in [company.street, company.street2, company.zip, company.city] if p]
            company_address = ' '.join(parts)

        department = ''
        dept_id = _id(emp_data.get('department_id'))
        if dept_id:
            department = self.env['hr.department'].sudo().browse(dept_id).name or ''

        # Salaire net contrat
        salary_net_contract = ''
        if contract_id:
            contract = self.env['hr.contract'].sudo().browse(contract_id)
            if contract.salary_net:
                salary_net_contract = self._format_monetary(contract.salary_net)

        # Dictionnaire des remplacements
        replacements = {
            '{{employee.name}}': dget(emp_data, 'name'),
            '{{employee.job_title}}': dget(emp_data, 'job_title'),
            '{{employee.department}}': department,
            '{{employee.acc_number}}': bank_account.acc_number or '',
            '{{employee.agence}}': bank_account.agence or '',
            '{{employee.bank}}': bank_name,
            '{{employee.email}}': dget(emp_data, 'work_email'),
            '{{employee.phone}}': dget(emp_data, 'mobile_phone'),
            '{{employee.private_street}}': dget(emp_data, 'private_street'),
            '{{employee.private_street2}}': dget(emp_data, 'private_street2'),
            '{{employee.private_zip}}': dget(emp_data, 'private_zip'),
            '{{employee.private_city}}': dget(emp_data, 'private_city'),
            '{{employee.id_number}}': dget(emp_data, 'identification_id'),
            '{{employee.cnss_number}}': dget(emp_data, 'ssnid'),
            '{{employee.hire_date}}': contract_date_str,
            '{{employee.ssnid}}': dget(emp_data, 'ssnid'),
            '{{gender}}': 'Mr' if dget(emp_data, 'gender') == 'male' else 'Mme',
            '{{employee.birth_date}}': self._get_birth_date(emp_data),

            '{{today_date}}': datetime.now().strftime('%d/%m/%Y'),
            '{{today_date_long}}': datetime.now().strftime('%d %B %Y'),

            '{{company_name}}': company_name,
            '{{company_address}}': company_address,
            '{{company_city}}': company_city,

            '{{contract_date}}': contract_date_str,

            '{{salary.base}}': self._get_salary_line(emp, 'BASE'),
            '{{salary.brut}}': self._get_salary_line(emp, 'GROSS'),
            '{{salary.amo}}': self._get_salary_line(emp, 'AMO'),
            '{{salary.cnss}}': self._get_salary_line(emp, 'CNSSE'),
            '{{salary.cimr}}': self._get_salary_line(emp, 'CIMRE'),
            '{{salary.amc}}': self._get_salary_line(emp, 'AMC_SAL'),
            '{{salary.igr}}': self._get_salary_line(emp, 'IR'),
            '{{salary.frais_pro}}': self._get_salary_line(emp, 'FRPRO'),
            '{{salary.net}}': self._get_salary_line(emp, 'NET'),
            '{{salary.note_frais}}': self._get_salary_line(emp, 'NOTE_FRAIS'),

            '{{salary.net_contract}}': salary_net_contract,
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value or ''))

        return content

    # --- Fonctions Helpers ---
    def _get_gender_display(self, employee):
        if hasattr(employee, 'gender'):
            return 'Mr' if employee.gender == 'male' else 'Mme'
        return 'Mr'

    def _get_birth_date(self, emp_data):
        if emp_data.get('birthday'):
            birthday = emp_data['birthday']
            if hasattr(birthday, 'strftime'):
                return birthday.strftime('%d-%m-%Y')
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
