# Installation & Configuration Guide
## Employee Document Management Module

### Prerequisites
- Odoo 18.0 or higher
- HR module installed
- Payroll module installed

### Installation Steps

#### 1. Copy the Module
```bash
cp -r hr_employee_documents /opt/GetapERP/GetapERP-V18/extra-addons/GetapPRO/Payroll/
```

#### 2. Update Module List
1. Navigate to **Apps > Update Apps List** in Odoo
2. Wait for the update to complete

#### 3. Install the Module
1. Search for "Employee Document Management" in Apps
2. Click on the module card
3. Click **Install** button

#### 4. Verify Installation
- Check that no errors appear during installation
- Navigate to **Human Resources > Employee Documents**
- Verify menu items are visible

### Initial Configuration

#### Step 1: Configure Document Types
1. Go to **Human Resources > Employee Documents > Document Types**
2. Review the pre-configured document types
3. Create additional types if needed:
   - Click **Create**
   - Enter Name (e.g., "Health Insurance Certificate")
   - Enter Code (e.g., "HEALTH_INS")
   - Set Approval Requirements if needed
   - Save

#### Step 2: Set Up User Access
Document access is controlled through groups:
- **HR Manager**: `hr.group_hr_manager`
- **HR Officer**: `hr.group_hr_officer`

To grant access:
1. Go to **Settings > Users & Companies > Users**
2. Select a user
3. In the **Access Rights** section, assign them to:
   - **Human Resources / Manager** (for full access)
   - **Human Resources / Officer** (for document management)

#### Step 3: Test the Module
1. Create a test employee if needed
2. Upload a sample document:
   - Go to **Human Resources > Employee Documents > Documents**
   - Click **Create**
   - Fill in test data
   - Save
3. Verify the document appears in the employee's profile

### Usage Scenarios

#### Scenario 1: Upload Work Certificate
1. Employee info: John Doe
2. Go to **Create** in Employee Documents
3. Select John Doe
4. Document Type: "Work Certificate"
5. Upload PDF file
6. Set Issue Date
7. Set Expiry Date (optional)
8. Click **Save**

#### Scenario 2: Approve Documents
1. Go to **Employee Documents**
2. Filter by "Pending Approval"
3. Open a document
4. Click **Approve** button
5. Document becomes visible to employee

#### Scenario 3: Reject Documents
1. Go to **Employee Documents**
2. Open pending document
3. Click **Reject** button
4. Enter rejection reason
5. Click **Reject** in wizard
6. Document marked as rejected

#### Scenario 4: Employee Views Own Documents
1. Employee logs in to Odoo
2. Goes to **Human Resources > Employees**
3. Clicks on their profile
4. Opens **Documents** tab
5. Views approved documents
6. Can download documents

### Advanced Configuration

#### Custom Document Types
To add new document types:
1. Go to **Employee Documents > Document Types**
2. Click **Create**
3. Fill in details:
   ```
   Name: Custom Type
   Code: CUSTOM_TYPE
   Require Manager Approval: Yes/No
   Description: Description of document
   ```

#### Approval Workflows
Some document types can require approval before being visible:
1. Edit a Document Type
2. Check "Require Manager Approval"
3. Save
4. Now all documents of this type need approval

#### Bulk Operations
Currently supports:
- Download individual documents
- Print documents as PDF
- Filter and group documents
- Export to spreadsheet

### Troubleshooting

#### Documents Not Visible to Employee
**Solution:** Check the "Visible to Employee" checkbox in the document form

#### Cannot Upload File
**Solutions:**
1. Check file size limits in Odoo settings
2. Verify file format is supported (PDF, DOCX, etc.)
3. Check user has create permissions

#### Permission Denied Errors
**Solutions:**
1. Verify user belongs to correct groups (HR Manager or HR Officer)
2. Check Record Rules haven't blocked access
3. Verify employee relationships are set correctly

#### Approval Button Grayed Out
**Solutions:**
1. Document must be in "Draft" status
2. User must have HR Manager role
3. Check record rules

### Performance Optimization

#### For Large File Storage
1. Configure external file storage (S3, etc.)
2. Implement file compression policy
3. Archive old documents

#### Database Optimization
1. Regularly archive expired documents
2. Delete rejected documents after review period
3. Create indexes on frequently searched fields

### Security Considerations

1. **Access Control**: Documents are controlled by record rules
2. **File Security**: Files stored in Odoo database
3. **Audit Trail**: All changes tracked in chatter
4. **Sensitive Info**: Use Internal Notes for manager-only information

### Backup & Recovery

#### Daily Backup
Include these directories:
- `/opt/GetapERP/GetapERP-V18/extra-addons/GetapPRO/Payroll/hr_employee_documents/`
- Odoo database

#### Recovery Steps
1. Restore database
2. Copy module files
3. Update module list
4. Reinstall module if needed

### Regular Maintenance

#### Weekly Tasks
- Review pending approvals
- Archive expired documents

#### Monthly Tasks
- Review document statistics
- Update document type configurations
- Clean up rejected documents

#### Yearly Tasks
- Archive old documents
- Review security policies
- Update module to latest version

### Integration with Other Modules

#### HR Module
- Employee information automatically available
- Manager hierarchy used for approvals
- Department information displayed

#### Payroll Module
- Documents can be tied to salary cycles
- Certificates needed for payroll processing
- Integration ready for future enhancements

#### Email/Notifications
- Status changes sent via chatter
- Notifications to managers
- Employee notifications about new documents

### Support & Issues

For technical support, contact:
- Email: support@getap.pro
- Website: https://www.getap.pro

### Changelog

**Version 18.0.1.0.0 (Initial Release)**
- Core document management features
- Approval workflow
- Document types and categorization
- Employee integration
- Reports and analytics
- Security and access control
