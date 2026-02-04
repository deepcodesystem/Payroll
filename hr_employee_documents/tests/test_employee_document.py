# -*- coding: utf-8 -*-
from odoo.tests import common
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import base64


class TestEmployeeDocument(common.TransactionCase):

    def setUp(self):
        super().setUp()

        # Create test employee
        self.employee = self.env['hr.employee'].create({
            'name': 'John Doe',
            'department_id': self.env['hr.department'].create({'name': 'IT'}).id,
        })

        # Create test document type
        self.doc_type = self.env['document.type'].create({
            'name': 'Work Certificate',
            'code': 'WORK_CERT',
            'description': 'Work certificate test',
        })

        # Create test file content
        self.test_file = base64.b64encode(b'Test PDF content')

    def test_create_document(self):
        """Test creating a simple document"""
        document = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Test Work Certificate',
            'document_file': self.test_file,
            'issue_date': date.today(),
        })

        self.assertEqual(document.state, 'draft')
        self.assertEqual(document.employee_id, self.employee)
        self.assertEqual(document.document_type_id, self.doc_type)

    def test_document_file_size(self):
        """Test that file size is calculated correctly"""
        document = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Test File Size',
            'document_file': self.test_file,
        })

        self.assertGreater(document.file_size, 0)

    def test_expiry_date_validation(self):
        """Test that expiry date must be after issue date"""
        today = date.today()

        with self.assertRaises(ValidationError):
            self.env['employee.document'].create({
                'employee_id': self.employee.id,
                'document_type_id': self.doc_type.id,
                'name': 'Invalid Date',
                'document_file': self.test_file,
                'issue_date': today,
                'expiry_date': today - timedelta(days=1),
            })

    def test_document_approval_workflow(self):
        """Test document approval workflow"""
        document = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Document for Approval',
            'document_file': self.test_file,
        })

        # Submit for approval
        document.action_submit_for_approval()
        self.assertEqual(document.state, 'pending')

        # Approve
        document.action_approve()
        self.assertEqual(document.state, 'approved')
        self.assertTrue(document.approval_date)

    def test_document_rejection(self):
        """Test document rejection workflow"""
        document = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Document for Rejection',
            'document_file': self.test_file,
        })

        document.action_submit_for_approval()
        self.assertEqual(document.state, 'pending')

        # Create rejection reason
        reject_wizard = self.env['employee.document.reject.wizard'].create({
            'document_id': document.id,
            'rejection_reason': 'Invalid document',
            'notify_employee': True,
        })

        reject_wizard.action_reject()
        self.assertEqual(document.state, 'rejected')
        self.assertEqual(document.rejection_reason, 'Invalid document')

    def test_document_expiry_check(self):
        """Test document expiry status"""
        today = date.today()

        # Not expired document
        document1 = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Valid Document',
            'document_file': self.test_file,
            'issue_date': today,
            'expiry_date': today + timedelta(days=30),
        })

        self.assertFalse(document1.is_expired)

        # Expired document
        document2 = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Expired Document',
            'document_file': self.test_file,
            'issue_date': today - timedelta(days=60),
            'expiry_date': today - timedelta(days=1),
        })

        self.assertTrue(document2.is_expired)

    def test_manager_assignment(self):
        """Test that manager is automatically assigned"""
        manager = self.env['hr.employee'].create({
            'name': 'Manager',
            'department_id': self.env['hr.department'].create({'name': 'Management'}).id,
        })

        self.employee.parent_id = manager

        document = self.env['employee.document'].create({
            'employee_id': self.employee.id,
            'document_type_id': self.doc_type.id,
            'name': 'Test Manager Assignment',
            'document_file': self.test_file,
        })

        self.assertEqual(document.manager_id, manager)

    def test_get_documents_by_type(self):
        """Test searching documents by type"""
        # Create multiple documents
        for i in range(3):
            self.env['employee.document'].create({
                'employee_id': self.employee.id,
                'document_type_id': self.doc_type.id,
                'name': f'Document {i}',
                'document_file': self.test_file,
            })

        # Get documents by type
        docs = self.env['employee.document'].get_documents_by_type(
            self.employee.id,
            self.doc_type.id
        )

        self.assertEqual(len(docs), 3)


class TestDocumentType(common.TransactionCase):

    def test_create_document_type(self):
        """Test creating a document type"""
        doc_type = self.env['document.type'].create({
            'name': 'Test Type',
            'code': 'TEST_TYPE',
            'description': 'A test document type',
        })

        self.assertEqual(doc_type.name, 'Test Type')
        self.assertEqual(doc_type.code, 'TEST_TYPE')
        self.assertTrue(doc_type.active)

    def test_unique_code_constraint(self):
        """Test that document type code is unique"""
        self.env['document.type'].create({
            'name': 'Type 1',
            'code': 'UNIQUE_CODE',
        })

        with self.assertRaises(Exception):  # IntegrityError
            self.env['document.type'].create({
                'name': 'Type 2',
                'code': 'UNIQUE_CODE',
            })
