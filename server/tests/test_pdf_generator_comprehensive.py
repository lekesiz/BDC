"""Comprehensive tests for PDF generator utility."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import BytesIO
import datetime
import os

from app.utils.pdf_generator import (
    PDFGenerator,
    generate_evaluation_report,
    generate_beneficiary_report,
    generate_report_pdf
)


class TestPDFGenerator:
    """Test the PDFGenerator class."""

    def test_init(self):
        """Test PDFGenerator initialization."""
        # Act
        pdf = PDFGenerator("Test Title", "Test Author")
        
        # Assert
        assert pdf.title == "Test Title"
        assert pdf.author == "Test Author"
        assert isinstance(pdf.buffer, BytesIO)
        assert hasattr(pdf, 'doc')
        assert hasattr(pdf, 'styles')
        assert hasattr(pdf, 'elements')
        assert len(pdf.elements) == 0

    def test_setup_custom_styles(self):
        """Test custom styles setup."""
        # Act
        pdf = PDFGenerator("Test")
        
        # Assert - check that custom styles exist
        assert 'Heading1' in pdf.styles
        assert 'Heading2' in pdf.styles
        assert 'Heading3' in pdf.styles
        assert 'Normal' in pdf.styles
        assert 'Italic' in pdf.styles
        assert 'Bold' in pdf.styles

    def test_add_title(self):
        """Test adding title to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_title("My Title")
        
        # Assert
        assert len(pdf.elements) == 2
        # First element should be a Paragraph, second a Spacer
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    def test_add_subtitle(self):
        """Test adding subtitle to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_subtitle("My Subtitle")
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    def test_add_heading(self):
        """Test adding heading to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_heading("My Heading")
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    def test_add_paragraph(self):
        """Test adding paragraph to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_paragraph("My paragraph text")
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    def test_add_bold_text(self):
        """Test adding bold text to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_bold_text("Bold text")
        
        # Assert
        assert len(pdf.elements) == 1
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'

    def test_add_italic_text(self):
        """Test adding italic text to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_italic_text("Italic text")
        
        # Assert
        assert len(pdf.elements) == 1
        assert pdf.elements[0].__class__.__name__ == 'Paragraph'

    def test_add_spacer(self):
        """Test adding spacer to document."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_spacer()
        
        # Assert
        assert len(pdf.elements) == 1
        assert pdf.elements[0].__class__.__name__ == 'Spacer'

    def test_add_spacer_custom_height(self):
        """Test adding spacer with custom height."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_spacer(1.5)
        
        # Assert
        assert len(pdf.elements) == 1
        assert pdf.elements[0].__class__.__name__ == 'Spacer'

    def test_add_table_default_style(self):
        """Test adding table with default style."""
        # Arrange
        pdf = PDFGenerator("Test")
        data = [['Header1', 'Header2'], ['Data1', 'Data2']]
        
        # Act
        pdf.add_table(data)
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Table'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    def test_add_table_custom_style(self):
        """Test adding table with custom style."""
        # Arrange
        pdf = PDFGenerator("Test")
        data = [['Header1', 'Header2'], ['Data1', 'Data2']]
        from reportlab.lib import colors
        from reportlab.platypus import TableStyle
        custom_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ])
        col_widths = [100, 150]
        
        # Act
        pdf.add_table(data, col_widths=col_widths, style=custom_style)
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Table'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    @patch('os.path.exists')
    def test_add_image_exists(self, mock_exists):
        """Test adding image when file exists."""
        # Arrange
        pdf = PDFGenerator("Test")
        mock_exists.return_value = True
        
        # Act
        pdf.add_image('/path/to/image.png', width=100, height=50)
        
        # Assert
        assert len(pdf.elements) == 2
        assert pdf.elements[0].__class__.__name__ == 'Image'
        assert pdf.elements[1].__class__.__name__ == 'Spacer'

    @patch('os.path.exists')
    def test_add_image_not_exists(self, mock_exists):
        """Test adding image when file doesn't exist."""
        # Arrange
        pdf = PDFGenerator("Test")
        mock_exists.return_value = False
        
        # Act
        pdf.add_image('/path/to/missing.png')
        
        # Assert
        assert len(pdf.elements) == 0  # No elements added

    def test_add_page_break(self):
        """Test adding page break."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        pdf.add_page_break()
        
        # Assert
        assert len(pdf.elements) == 1
        assert pdf.elements[0].__class__.__name__ == 'Spacer'

    def test_add_footer(self):
        """Test adding footer returns a function."""
        # Arrange
        pdf = PDFGenerator("Test")
        
        # Act
        footer_func = pdf.add_footer()
        
        # Assert
        assert callable(footer_func)

    def test_build(self):
        """Test building the PDF document."""
        # Arrange
        pdf = PDFGenerator("Test")
        pdf.add_title("Test Title")
        pdf.add_paragraph("Test content")
        
        # Act
        result = pdf.build()
        
        # Assert
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestGenerateEvaluationReport:
    """Test the generate_evaluation_report function."""

    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_evaluation_report_complete(self, mock_pdf_class):
        """Test generating complete evaluation report."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        
        evaluation = Mock()
        evaluation.title = "Test Evaluation"
        evaluation.date_created = datetime.datetime(2025, 5, 26)
        evaluation.status = "completed"
        evaluation.score = 85
        evaluation.summary = "Test summary"
        evaluation.recommendations = "Test recommendations"
        
        question1 = Mock()
        question1.text = "Question 1?"
        answer1 = Mock()
        answer1.text = "Answer 1"
        answer1.score = 10
        question1.answer = answer1
        
        question2 = Mock()
        question2.text = "Question 2?"
        question2.answer = None
        
        evaluation.questions = [question1, question2]
        
        user = Mock()
        user.first_name = "John"
        user.last_name = "Doe"
        
        beneficiary = Mock()
        beneficiary.first_name = "Jane"
        beneficiary.last_name = "Smith"
        beneficiary.email = "jane@example.com"
        beneficiary.status = "active"
        
        # Act
        result = generate_evaluation_report(evaluation, user, beneficiary)
        
        # Assert
        assert result == b'PDF content'
        mock_pdf.add_title.assert_called_with("Evaluation Report")
        mock_pdf.add_subtitle.assert_any_call("Beneficiary Information")
        mock_pdf.add_subtitle.assert_any_call("Evaluation Details")
        mock_pdf.add_subtitle.assert_any_call("Responses")
        mock_pdf.add_subtitle.assert_any_call("Summary")
        mock_pdf.add_subtitle.assert_any_call("Recommendations")
        mock_pdf.add_heading.assert_any_call("Question 1: Question 1?")
        mock_pdf.add_heading.assert_any_call("Question 2: Question 2?")
        mock_pdf.add_italic_text.assert_called_with("No answer provided")

    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_evaluation_report_minimal(self, mock_pdf_class):
        """Test generating minimal evaluation report."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        
        evaluation = Mock()
        evaluation.title = "Test Evaluation"
        evaluation.date_created = datetime.datetime(2025, 5, 26)
        evaluation.status = "pending"
        evaluation.score = None
        evaluation.questions = []
        
        # Remove summary and recommendations
        del evaluation.summary
        del evaluation.recommendations
        
        user = Mock()
        user.first_name = "John"
        user.last_name = "Doe"
        
        beneficiary = Mock()
        beneficiary.first_name = "Jane"
        beneficiary.last_name = "Smith"
        beneficiary.email = "jane@example.com"
        beneficiary.status = "active"
        
        # Act
        result = generate_evaluation_report(evaluation, user, beneficiary)
        
        # Assert
        assert result == b'PDF content'
        # Should not call summary/recommendations
        assert not any(call[0][0] == "Summary" for call in mock_pdf.add_subtitle.call_args_list)
        assert not any(call[0][0] == "Recommendations" for call in mock_pdf.add_subtitle.call_args_list)


class TestGenerateBeneficiaryReport:
    """Test the generate_beneficiary_report function."""

    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_beneficiary_report_with_evaluations(self, mock_pdf_class):
        """Test generating beneficiary report with evaluations."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        
        beneficiary = Mock()
        beneficiary.first_name = "Jane"
        beneficiary.last_name = "Smith"
        beneficiary.email = "jane@example.com"
        beneficiary.status = "active"
        beneficiary.summary = "Beneficiary summary"
        beneficiary.recommendations = "Beneficiary recommendations"
        
        trainer = Mock()
        trainer.first_name = "Trainer"
        trainer.last_name = "Name"
        trainer.email = "trainer@example.com"
        beneficiary.trainer = trainer
        
        eval1 = Mock()
        eval1.title = "Evaluation 1"
        eval1.date_created = datetime.datetime(2025, 5, 20)
        eval1.status = "completed"
        eval1.score = 90
        
        eval2 = Mock()
        eval2.title = "Evaluation 2"
        eval2.date_created = datetime.datetime(2025, 5, 25)
        eval2.status = "completed"
        eval2.score = 85
        
        evaluations = [eval1, eval2]
        
        user = Mock()
        user.first_name = "John"
        user.last_name = "Doe"
        
        # Act
        result = generate_beneficiary_report(beneficiary, evaluations, user)
        
        # Assert
        assert result == b'PDF content'
        mock_pdf.add_title.assert_called_with("Beneficiary Progress Report")
        mock_pdf.add_subtitle.assert_any_call("Beneficiary Information")
        mock_pdf.add_subtitle.assert_any_call("Trainer Information")
        mock_pdf.add_subtitle.assert_any_call("Evaluations Summary")
        mock_pdf.add_subtitle.assert_any_call("Summary")
        mock_pdf.add_subtitle.assert_any_call("Recommendations")
        
        # Check table was added
        table_data = mock_pdf.add_table.call_args[0][0]
        assert table_data[0] == ['Title', 'Date', 'Status', 'Score']
        assert len(table_data) == 3  # Header + 2 evaluations
        
        # Check overall progress calculation
        paragraph_calls = [call[0][0] for call in mock_pdf.add_paragraph.call_args_list]
        assert any("<b>Overall Progress:</b> 2/2 evaluations completed" in call for call in paragraph_calls)
        assert any("<b>Average Score:</b> 87.5%" in call for call in paragraph_calls)

    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_beneficiary_report_no_evaluations(self, mock_pdf_class):
        """Test generating beneficiary report without evaluations."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        
        beneficiary = Mock()
        beneficiary.first_name = "Jane"
        beneficiary.last_name = "Smith"
        beneficiary.email = "jane@example.com"
        beneficiary.status = "active"
        
        # No trainer, summary, or recommendations
        beneficiary.trainer = None
        del beneficiary.summary
        del beneficiary.recommendations
        
        evaluations = []
        
        user = Mock()
        user.first_name = "John"
        user.last_name = "Doe"
        
        # Act
        result = generate_beneficiary_report(beneficiary, evaluations, user)
        
        # Assert
        assert result == b'PDF content'
        
        # Should not add trainer section
        assert not any(call[0][0] == "Trainer Information" for call in mock_pdf.add_subtitle.call_args_list)
        
        # Should add "No evaluations available"
        paragraph_calls = [call[0][0] for call in mock_pdf.add_paragraph.call_args_list]
        assert any("No evaluations available." in call for call in paragraph_calls)


class TestGenerateReportPDF:
    """Test the generate_report_pdf function."""

    @patch('app.utils.pdf_generator.PDFGenerator')
    @patch('app.utils.pdf_generator.A4')
    def test_generate_report_pdf_with_data(self, mock_a4, mock_pdf_class):
        """Test generating report PDF with data."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        mock_a4.__getitem__.return_value = 595  # A4 width
        
        template_data = {
            'title': 'Test Report',
            'description': 'This is a test report',
            'generated_at': '2025-05-26 10:00:00',
            'generated_by': 'Admin User',
            'report_type': 'Analytics',
            'data': [
                {'name': 'Item 1', 'value': 100, 'status': 'Active'},
                {'name': 'Item 2', 'value': 200, 'status': 'Inactive'}
            ]
        }
        
        # Act
        result = generate_report_pdf(template_data)
        
        # Assert
        assert result == b'PDF content'
        mock_pdf.add_title.assert_called_with('Test Report')
        mock_pdf.add_paragraph.assert_any_call('This is a test report')
        mock_pdf.add_subtitle.assert_any_call("Report Information")
        mock_pdf.add_subtitle.assert_any_call("Report Data")
        
        # Check table data
        table_call = mock_pdf.add_table.call_args
        table_data = table_call[0][0]
        assert table_data[0] == ['name', 'value', 'status']
        assert table_data[1] == ['Item 1', '100', 'Active']
        assert table_data[2] == ['Item 2', '200', 'Inactive']
        
        # Check column widths were calculated
        assert table_call[1]['col_widths'] is not None

    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_report_pdf_minimal(self, mock_pdf_class):
        """Test generating report PDF with minimal data."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        
        template_data = {
            'title': 'Empty Report'
        }
        
        # Act
        result = generate_report_pdf(template_data)
        
        # Assert
        assert result == b'PDF content'
        mock_pdf.add_title.assert_called_with('Empty Report')
        
        # Should add "No data available"
        paragraph_calls = [call[0][0] for call in mock_pdf.add_paragraph.call_args_list]
        assert any("No data available for this report." in call for call in paragraph_calls)

    @patch('app.utils.pdf_generator.PDFGenerator')
    @patch('app.utils.pdf_generator.A4')
    def test_generate_report_pdf_column_width_calculation(self, mock_a4, mock_pdf_class):
        """Test column width calculation in report PDF."""
        # Arrange
        mock_pdf = MagicMock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b'PDF content'
        mock_a4.__getitem__.return_value = 595  # A4 width
        
        template_data = {
            'data': [
                {'short': 'S', 'very_long_column_name': 'This is a very long value that should affect column width'}
            ]
        }
        
        # Act
        generate_report_pdf(template_data)
        
        # Assert
        table_call = mock_pdf.add_table.call_args
        col_widths = table_call[1]['col_widths']
        assert len(col_widths) == 2
        # Long column should have wider width
        assert col_widths[1] > col_widths[0]