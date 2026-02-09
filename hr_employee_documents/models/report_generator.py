# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import base64

class ReportTemplateGenerator(models.TransientModel):
    _name = 'hr.report.template.generator'
    _description = 'Report Template Generator'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    template_id = fields.Many2one('hr.employee.report.template', string='Template', required=True)

    def generate_report(self):
        self.ensure_one()
        
        # 1. Génération du contenu HTML (en format texte String)
        content = self._get_filled_content()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; font-size: 14px; line-height: 1.6; }}
        .page {{ padding: 20px; }}
        .underline {{ text-decoration: underline; }}
        h1 {{ text-align: center; font-size: 22px; }}
    </style>
</head>
<body>
    <div class="page">
        {content}
    </div>
</body>
</html>"""

        try:
            # 2. Conversion en PDF
            # IMPORTANT : On passe html_content tel quel (String), PAS de .encode()
            pdf_bytes = self.env['ir.actions.report']._run_wkhtmltopdf([html_content])

            if not pdf_bytes:
                raise UserError(_("Le générateur PDF a renvoyé un fichier vide."))

            # 3. Création de l'attachement
            emp_name = str(self.employee_id.name).replace(' ', '_')
            filename = f"{self.template_id.code or 'DOC'}_{emp_name}.pdf"

            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.b64encode(pdf_bytes),
                'mimetype': 'application/pdf',
                'type': 'binary',
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except Exception as e:
            # C'est ici que l'erreur s'affichera si wkhtmltopdf n'est pas installé sur le serveur
            raise UserError(_("Erreur lors de la génération du PDF : %s") % str(e))

    def _get_filled_content(self):
        """Remplit le template avec les données de l'employé (Retourne un String)"""
        content = self.template_id.template_content or ""
        employee = self.employee_id
        
        # Exemple de remplissage minimal (à compléter avec vos besoins)
        replacements = {
            '{{employee.name}}': employee.name or '',
            '{{today_date}}': datetime.now().strftime('%d/%m/%Y'),
            '{{company_name}}': employee.company_id.name or '',
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))
            
        return content
