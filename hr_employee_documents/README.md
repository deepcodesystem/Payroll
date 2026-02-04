# Employee Document Management Module

## Description
This module provides a comprehensive solution for managing and distributing employee documents through Odoo. It allows HR managers and responsible persons to upload, manage, approve, and control access to various employee documents.

## Features

### Document Management
- **Upload Documents**: Upload various types of employee documents (PDF, Word, etc.)
- **Organize by Type**: Categorize documents using predefined document types
- **Version History**: Track all document uploads and modifications
- **File Metadata**: Automatic tracking of file size, type, and upload date

### Document Types
The module comes with predefined document types:
- **Work Certificate**: Official certificate of employment/work attestation
- **Experience Certificate**: Certificate proving work experience and competencies
- **Salary Certificate**: Certificate proving salary/income
- **Training Certificate**: Professional development and training records
- **Medical Record**: Health-related documents
- **Performance Review**: Annual performance evaluation documents
- **Other Documents**: Miscellaneous documents

### Approval Workflow
- **Draft Status**: Documents start in draft status
- **Submit for Approval**: Submit documents requiring manager approval
- **Approval/Rejection**: Managers can approve or reject documents with detailed reasons
- **Status Tracking**: Complete audit trail of all status changes

### Access Control
- **Role-Based Access**: Different permissions for HR managers, officers, and employees
- **Visibility Control**: Control which documents are visible to employees
- **Manager Assignment**: Automatic assignment of documents to employee managers
- **Approval Requirements**: Configurable approval requirements by document type

### Search & Filtering
- **Advanced Search**: Search by employee, document type, dates, status
- **Grouped Views**: Group documents by employee, type, status, or manager
- **Status Filters**: Quick filters for draft, pending, approved, rejected documents
- **Expiry Tracking**: Identify expired documents

### Additional Features
- **Expiry Dates**: Track document expiration dates
- **Document Download**: Easy download of documents
- **Notes & Comments**: Add internal notes and employee comments
- **Email Notifications**: Notify employees of document status changes
- **Integration**: Seamlessly integrates with HR and Payroll modules

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r hr_employee_documents /path/to/odoo/addons/
   ```

2. Update module list in Odoo:
   - Go to Apps > Update Apps List

3. Install the module:
   - Search for "Employee Document Management"
   - Click Install

## Usage

### For HR Managers

#### Uploading a Document
1. Navigate to **Human Resources > Employee Documents > Documents**
2. Click **Create**
3. Fill in the document details:
   - Select the employee
   - Choose document type
   - Enter document title
   - Upload the file
   - Set issue and expiry dates
4. Save the document

#### Approving Documents
1. Navigate to **Human Resources > Employee Documents > Documents**
2. Filter by "Pending Approval" status
3. Open a document
4. Click **Approve** to accept or **Reject** to decline
5. If rejecting, provide a reason

#### Managing Document Types
1. Navigate to **Human Resources > Employee Documents > Document Types**
2. Create new types or modify existing ones
3. Set whether manager approval is required

### For Employees

#### Viewing Documents
1. Navigate to **Human Resources > Employees**
2. Select your employee profile
3. Go to the **Documents** tab to view all uploaded documents

#### Downloading Documents
- Click on any document in the list
- Click the **Download** button

## Technical Details

### Models
- **document.type**: Categories for employee documents
- **employee.document**: Individual employee documents
- **employee.document.reject.wizard**: Transient model for document rejection

### Security
- Access controlled via security groups
- HR Managers and officers have full access
- All users can view their own documents

### Fields

#### Document Type
- Name, Code, Description
- Approval requirement flag
- Sequence and color coding

#### Employee Document
- Employee relationship
- Document type
- File storage and metadata
- Issue and expiry dates
- Status and approval tracking
- Visibility controls
- Internal notes

## API Usage

### Create Document
```python
document = self.env['employee.document'].create({
    'employee_id': employee_id,
    'document_type_id': doc_type_id,
    'name': 'Work Certificate',
    'document_file': base64_content,
    'issue_date': date.today(),
})
```

### Search Documents
```python
documents = self.env['employee.document'].search([
    ('employee_id', '=', employee_id),
    ('state', '=', 'approved'),
])
```

### Get Documents by Type
```python
docs = document.get_documents_by_type(employee_id, doc_type_id)
```

## Support & Contribution
For issues, feature requests, or contributions, please contact GetapPRO.

## License
LGPL-3

## Author
GetapPRO
Website: https://www.getap.pro
