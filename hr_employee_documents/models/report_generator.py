# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import base64
import io
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
        """Generate and download PDF report using Odoo Qweb"""
        self.ensure_one()
        if not self.employee_id:
            raise UserError(_('Please select an employee'))
        if not self.template_id:
            raise UserError(_('Please select a template'))
        try:
            # Get filled content
            content = self._get_filled_content()
            # Create HTML content for the report
            html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.template_id.name}</title>
    <style>
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        .page {{
            page-break-after: always;
            padding: 20px;
            margin: 0;
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
        h1 {{ font-size: 24px; margin-bottom: 15px; text-align: center; }}
        h2 {{ font-size: 18px; margin-bottom: 12px; }}
        h3 {{ font-size: 14px; margin-bottom: 10px; }}
        p {{ margin: 5px 0; }}
        @page {{
            size: A4;
            margin: 20mm;
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
            # Use Odoo's Qweb engine to render the template
            try:
                qweb = self.env['ir.qweb']
                # Render the template using Qweb
                pdf_content = qweb._render('hr_employee_documents.report_employee_document_template', {
                    'doc': self.employee_id,
                    'docs': [self.employee_id],
                    'doc_content': html_content,
                }, minimal_qcontext=True)
                # The result should be PDF bytes from Qweb rendering
                if isinstance(pdf_content, str):
                    # If it's HTML string, we need to convert it
                    # Use Odoo's built-in PDF generation
                    pdf_bytes = self._html_to_pdf(pdf_content)
                else:
                    pdf_bytes = pdf_content
            except Exception as e:
                # Fallback: If Qweb fails, generate simple PDF from HTML
                pdf_bytes = self._html_to_pdf(html_content)
            # Create filename
            emp_name = str(self.employee_id.name).replace(' ', '_').replace('/', '-').replace('\\', '-')
            template_code = str(self.template_id.code).replace(' ', '_')
            filename = f"{template_code}_{emp_name}.pdf"
            # Ensure pdf_bytes is in the right format
            if isinstance(pdf_bytes, str):
                pdf_bytes = pdf_bytes.encode('utf-8')
            # Create attachment for download
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(pdf_bytes),
                'type': 'binary',
                'mimetype': 'application/pdf',
            })
            # Return download URL
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
        except Exception as e:
            error_msg = str(e)
            raise UserError(_('Error generating report: %s') % error_msg)
   
    def _html_to_pdf(self, html_content):
        """Version stricte pour débogage : ne cache aucune erreur"""
        # On encode le HTML en bytes pour wkhtmltopdf
        html_encoded = html_content.encode('utf-8')
        
        # On utilise directement l'outil de base d'Odoo
        # Si ça échoue, Odoo affichera une erreur rouge à l'écran
        # ou une erreur détaillée dans les logs serveur
        pdf_bytes = self.env['ir.actions.report']._run_wkhtmltopdf([html_encoded])
        
        return pdf_bytes
        
    def _get_filled_content(self):
        """Fill template with employee data"""
        try:
            content = self.template_id.template_content or ''
            employee = self.employee_id
            if not content:
                return '<p>Template content is empty</p>'
            # Helper function to safely get attribute
            def safe_get(obj, attr, default=''):
                """Safely get an attribute value"""
                try:
                    if not obj:
                        return default
                    value = getattr(obj, attr, None)
                    if value is None or value is False:
                        return default
                    # If it's a many2one or other relational field with name
                    if hasattr(value, 'name'):
                        return str(value.name) if value.name else default
                    # Convert to string
                    return str(value) if value else default
                except Exception:
                    return default
            # Get date strings safely
            hire_date_str = ''
            try:
                if employee.create_date:
                    hire_date_str = employee.create_date.strftime('%d/%m/%Y')
            except Exception:
                pass
            contract_date_str = ''
            try:
                if employee.contract_id and employee.contract_id.date_start:
                    contract_date_str = employee.contract_id.date_start.strftime('%d/%m/%Y')
            except Exception:
                pass
            # Create replacements dictionary
            replacements = {
                # Employee basic info
                '{{employee.name}}': safe_get(employee, 'name', ''),
                '{{employee.job_title}}': safe_get(employee, 'job_title', ''),
                '{{employee.department}}': safe_get(employee.department_id, 'name', '') if employee.department_id else '',
                '{{employee.acc_number}}': safe_get(employee.bank_account_id, 'acc_number', '') if employee.bank_account_id else '',
                '{{employee.agence}}': safe_get(employee.bank_account_id, 'agence', '') if employee.bank_account_id else '',
                '{{employee.bank}}': safe_get(employee.bank_account_id.bank_id, 'name', '') if employee.bank_account_id.bank_id else '',
                '{{employee.email}}': safe_get(employee, 'work_email', ''),
                '{{employee.phone}}': safe_get(employee, 'mobile_phone', ''),
                '{{employee.street}}': safe_get(employee, 'street', ''),
                '{{employee.street2}}': safe_get(employee, 'street2', ''),
                '{{employee.city}}': safe_get(employee, 'city', ''),
                '{{employee.zip}}': safe_get(employee, 'zip', ''),
                '{{employee.address}}': safe_get(employee, 'street', ''),
                '{{employee.id_number}}': safe_get(employee, 'identification_id', ''),
                '{{employee.hire_date}}': hire_date_str,

                # Additional employee info for Attestation
                '{{gender}}': self._get_gender_display(employee),
                '{{employee.birth_date}}': self._get_birth_date(employee),
                '{{employee.cnss_number}}': safe_get(employee, 'sn_number', ''),

                # Dates
                '{{today_date}}': datetime.now().strftime('%d/%m/%Y'),
                '{{today_date_long}}': datetime.now().strftime('%d %B %Y'),
                '{{today_date_en}}': datetime.now().strftime('%m/%d/%Y'),

                # Company info
                '{{company_name}}': safe_get(employee.company_id, 'name', '') if employee.company_id else '',
                '{{company_email}}': safe_get(employee.company_id, 'email', '') if employee.company_id else '',
                '{{company_phone}}': safe_get(employee.company_id, 'phone', '') if employee.company_id else '',
                '{{company_address}}': self._get_company_address(employee),
                '{{company_city}}': self._get_company_city(employee),

                # Contract info
                '{{contract_date}}': contract_date_str,
            }
            # Replace all placeholders
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, str(value) if value else '')
            return content
        except Exception as e:
            return f'<p style="color: red;">Error filling template: {str(e)}</p>'

    def _get_gender_display(self, employee):
        """Get employee gender in French format (Mr/Mme)"""
        try:
            if hasattr(employee, 'gender'):
                if employee.gender == 'male':
                    return 'Mr'
                elif employee.gender == 'female':
                    return 'Mme'
            return 'Mr'
        except Exception:
            return 'Mr'

    def _get_birth_date(self, employee):
        """Get employee birth date formatted as DD-MM-YYYY"""
        try:
            if hasattr(employee, 'birthday') and employee.birthday:
                return employee.birthday.strftime('%d-%m-%Y')
            return ''
        except Exception:
            return ''

    def _get_company_address(self, employee):
        """Get company full address"""
        try:
            if employee.company_id:
                parts = []
                if hasattr(employee.company_id, 'street') and employee.company_id.street:
                    parts.append(employee.company_id.street)
                if hasattr(employee.company_id, 'street2') and employee.company_id.street2:
                    parts.append(employee.company_id.street2)
                if hasattr(employee.company_id, 'zip') and employee.company_id.zip:
                    parts.append(employee.company_id.zip)
                if hasattr(employee.company_id, 'city') and employee.company_id.city:
                    parts.append(employee.company_id.city)
                return ' '.join(parts)
            return ''
        except Exception:
            return ''

    def _get_company_city(self, employee):
        """Get company city"""
        try:
            if employee.company_id and hasattr(employee.company_id, 'city'):
                return employee.company_id.city or ''
            return ''
        except Exception:
            return ''

