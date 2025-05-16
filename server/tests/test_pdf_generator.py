"""Tests for PDF generator utility."""

import os
import datetime
from io import BytesIO
from unittest.mock import Mock, MagicMock, patch, call
import pytest
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas

from app.utils.pdf_generator import PDFGenerator, generate_evaluation_report, generate_beneficiary_report, generate_report_pdf


# Create a custom fixture for StyleSheet mock
def create_mock_style_sheet():
    """Create a mock stylesheet that properly handles the add() method."""
    mock_styles = MagicMock()
    existing_styles = {}
    
    # Pre-populate with base styles that PDFGenerator expects
    for style_name in ['Heading1', 'Heading2', 'Heading3', 'Normal', 'Italic', 'Bold', 'Title', 'BodyText']:
        mock_style = MagicMock(spec=ParagraphStyle)
        mock_style.name = style_name
        existing_styles[style_name] = mock_style
    
    # Mock the add method to check if style exists
    def mock_add(style):
        name = style.name
        # According to the PDF generator behavior, it tries to redefine existing styles
        # We should just update them rather than raise KeyError
        existing_styles[name] = style
        mock_styles[name] = style
    
    # Mock getitem to return existing styles
    def mock_getitem(key):
        if key in existing_styles:
            return existing_styles[key]
        return MagicMock()
    
    mock_styles.add = mock_add
    mock_styles.__getitem__ = mock_getitem
    mock_styles.__contains__ = lambda key: key in existing_styles
    
    # Attach the existing styles directly
    for name, style in existing_styles.items():
        setattr(mock_styles, name, style)
    
    return mock_styles


class TestPDFGenerator:
    """Test PDFGenerator class."""
    
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_init(self, mock_get_style_sheet):
        """Test PDF generator initialization."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report", author="Test Author")
        
        assert pdf.title == "Test Report"
        assert pdf.author == "Test Author"
        assert isinstance(pdf.buffer, BytesIO)
        assert isinstance(pdf.doc, SimpleDocTemplate)
        assert len(pdf.elements) == 0
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_init_default_author(self, mock_get_style_sheet):
        """Test PDF generator initialization with default author."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        
        assert pdf.title == "Test Report"
        assert pdf.author == "BDC System"
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_setup_custom_styles(self, mock_get_style_sheet):
        """Test custom styles setup."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        
        # Check if custom styles are added
        assert 'Heading1' in pdf.styles
        assert 'Heading2' in pdf.styles
        assert 'Heading3' in pdf.styles
        assert 'Normal' in pdf.styles
        assert 'Italic' in pdf.styles
        assert 'Bold' in pdf.styles
        
        # Verify style properties
        assert pdf.styles['Heading1'].fontSize == 16
        assert pdf.styles['Heading2'].fontSize == 14
        assert pdf.styles['Heading3'].fontSize == 12
        assert pdf.styles['Normal'].fontSize == 10
        assert pdf.styles['Bold'].fontName == 'Helvetica-Bold'
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_title(self, mock_get_style_sheet):
        """Test adding title to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_title("Test Title")
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Paragraph)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_subtitle(self, mock_get_style_sheet):
        """Test adding subtitle to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_subtitle("Test Subtitle")
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Paragraph)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_heading(self, mock_get_style_sheet):
        """Test adding heading to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_heading("Test Heading")
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Paragraph)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_paragraph(self, mock_get_style_sheet):
        """Test adding paragraph to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_paragraph("Test paragraph content")
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Paragraph)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_bold_text(self, mock_get_style_sheet):
        """Test adding bold text to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_bold_text("Bold text")
        
        assert len(pdf.elements) == 1
        assert isinstance(pdf.elements[0], Paragraph)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_italic_text(self, mock_get_style_sheet):
        """Test adding italic text to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_italic_text("Italic text")
        
        assert len(pdf.elements) == 1
        assert isinstance(pdf.elements[0], Paragraph)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_spacer(self, mock_get_style_sheet):
        """Test adding spacer to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_spacer()
        
        assert len(pdf.elements) == 1
        assert isinstance(pdf.elements[0], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_spacer_custom_height(self, mock_get_style_sheet):
        """Test adding spacer with custom height."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_spacer(height=1.5)
        
        assert len(pdf.elements) == 1
        assert isinstance(pdf.elements[0], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_table_default_style(self, mock_get_style_sheet):
        """Test adding table with default style."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        data = [['Header1', 'Header2'], ['Data1', 'Data2']]
        pdf.add_table(data)
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Table)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_table_custom_style(self, mock_get_style_sheet):
        """Test adding table with custom style."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        data = [['Header1', 'Header2'], ['Data1', 'Data2']]
        custom_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
        ])
        pdf.add_table(data, style=custom_style)
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Table)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_table_with_col_widths(self, mock_get_style_sheet):
        """Test adding table with column widths."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        data = [['Header1', 'Header2'], ['Data1', 'Data2']]
        col_widths = [5*cm, 10*cm]
        pdf.add_table(data, col_widths=col_widths)
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Table)
        
    @patch('os.path.exists')
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_image_exists(self, mock_get_style_sheet, mock_exists):
        """Test adding existing image to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        mock_exists.return_value = True
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_image("/path/to/image.png")
        
        assert len(pdf.elements) == 2
        assert isinstance(pdf.elements[0], Image)
        assert isinstance(pdf.elements[1], Spacer)
        
    @patch('os.path.exists')
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_image_not_exists(self, mock_get_style_sheet, mock_exists):
        """Test adding non-existing image to document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        mock_exists.return_value = False
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_image("/path/to/nonexistent.png")
        
        assert len(pdf.elements) == 0
        
    @patch('os.path.exists')
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_image_with_dimensions(self, mock_get_style_sheet, mock_exists):
        """Test adding image with custom dimensions."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        mock_exists.return_value = True
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_image("/path/to/image.png", width=10*cm, height=5*cm)
        
        assert len(pdf.elements) == 2
        img = pdf.elements[0]
        assert isinstance(img, Image)
        assert img.drawWidth == 10*cm
        assert img.drawHeight == 5*cm
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_page_break(self, mock_get_style_sheet):
        """Test adding page break."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_page_break()
        
        assert len(pdf.elements) == 1
        assert isinstance(pdf.elements[0], Spacer)
        
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_add_footer(self, mock_get_style_sheet):
        """Test adding footer."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        pdf = PDFGenerator(title="Test Report")
        footer_func = pdf.add_footer()
        
        assert callable(footer_func)
        
        # Test footer function
        mock_canvas = Mock()
        mock_doc = Mock()
        mock_doc.page = 1
        
        footer_func(mock_canvas, mock_doc)
        
        # Verify canvas methods were called
        mock_canvas.saveState.assert_called_once()
        mock_canvas.restoreState.assert_called_once()
        mock_canvas.setStrokeColor.assert_called_with(colors.grey)
        mock_canvas.setFont.assert_called_with('Helvetica', 8)
        
    @patch('datetime.datetime')
    @patch('app.utils.pdf_generator.getSampleStyleSheet')
    def test_build(self, mock_get_style_sheet, mock_datetime):
        """Test building PDF document."""
        # Use our mock style sheet
        mock_get_style_sheet.return_value = create_mock_style_sheet()
        
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0)
        
        pdf = PDFGenerator(title="Test Report")
        pdf.add_title("Test Title")
        pdf.add_paragraph("Test content")
        
        # Mock the document build method
        pdf.doc.build = Mock()
        
        result = pdf.build()
        
        # Verify build was called with proper arguments
        pdf.doc.build.assert_called_once()
        assert len(pdf.doc.build.call_args[0][0]) == 4  # Title + spacer + paragraph + spacer
        
        # Verify buffer operations
        assert pdf.buffer.closed
        

class TestEvaluationReport:
    """Test generate_evaluation_report function."""
    
    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_evaluation_report(self, mock_pdf_class):
        """Test generating evaluation report."""
        # Mock objects
        mock_evaluation = Mock()
        mock_evaluation.title = "Test Evaluation"
        mock_evaluation.date_created = datetime.datetime(2023, 1, 1)
        mock_evaluation.status = "completed"
        mock_evaluation.score = 85
        
        mock_question = Mock()
        mock_question.text = "Question 1?"
        mock_answer = Mock()
        mock_answer.text = "Answer 1"
        mock_answer.score = 10
        mock_question.answer = mock_answer
        
        mock_evaluation.questions = [mock_question]
        mock_evaluation.summary = "Test summary"
        mock_evaluation.recommendations = "Test recommendations"
        
        mock_user = Mock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        mock_beneficiary = Mock()
        mock_beneficiary.first_name = "Jane"
        mock_beneficiary.last_name = "Smith"
        mock_beneficiary.email = "jane@example.com"
        mock_beneficiary.status = "active"
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_evaluation_report(mock_evaluation, mock_user, mock_beneficiary)
        
        # Verify PDF generator was created correctly
        mock_pdf_class.assert_called_with("Evaluation Report - Jane Smith")
        
        # Verify methods were called
        mock_pdf.add_title.assert_called_with("Evaluation Report")
        mock_pdf.add_subtitle.assert_any_call("Beneficiary Information")
        mock_pdf.add_subtitle.assert_any_call("Evaluation Details")
        mock_pdf.add_subtitle.assert_any_call("Responses")
        mock_pdf.add_heading.assert_called_with("Question 1: Question 1?")
        mock_pdf.add_subtitle.assert_any_call("Summary")
        mock_pdf.add_subtitle.assert_any_call("Recommendations")
        
        assert result == b"PDF content"
        

class TestBeneficiaryReport:
    """Test generate_beneficiary_report function."""
    
    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_beneficiary_report_with_evaluations(self, mock_pdf_class):
        """Test generating beneficiary report with evaluations."""
        # Mock objects
        mock_user = Mock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        mock_beneficiary = Mock()
        mock_beneficiary.first_name = "Jane"
        mock_beneficiary.last_name = "Smith"
        mock_beneficiary.email = "jane@example.com"
        mock_beneficiary.status = "active"
        
        # Mock trainer
        mock_trainer = Mock()
        mock_trainer.first_name = "Bob"
        mock_trainer.last_name = "Jones"
        mock_trainer.email = "bob@example.com"
        mock_beneficiary.trainer = mock_trainer
        
        # Mock evaluations
        mock_eval1 = Mock()
        mock_eval1.title = "Evaluation 1"
        mock_eval1.date_created = datetime.datetime(2023, 1, 1)
        mock_eval1.status = "completed"
        mock_eval1.score = 80
        
        mock_eval2 = Mock()
        mock_eval2.title = "Evaluation 2"
        mock_eval2.date_created = datetime.datetime(2023, 1, 15)
        mock_eval2.status = "completed"
        mock_eval2.score = 90
        
        evaluations = [mock_eval1, mock_eval2]
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_beneficiary_report(mock_beneficiary, evaluations, mock_user)
        
        # Verify PDF generator was created correctly
        mock_pdf_class.assert_called_with("Beneficiary Report - Jane Smith")
        
        # Verify methods were called
        mock_pdf.add_title.assert_called_with("Beneficiary Progress Report")
        mock_pdf.add_subtitle.assert_any_call("Beneficiary Information")
        mock_pdf.add_subtitle.assert_any_call("Trainer Information")
        mock_pdf.add_subtitle.assert_any_call("Evaluations Summary")
        
        # Verify table was added
        mock_pdf.add_table.assert_called_once()
        table_data = mock_pdf.add_table.call_args[0][0]
        assert table_data[0] == ['Title', 'Date', 'Status', 'Score']
        assert table_data[1] == ['Evaluation 1', '2023-01-01', 'completed', '80%']
        assert table_data[2] == ['Evaluation 2', '2023-01-15', 'completed', '90%']
        
        assert result == b"PDF content"
        
    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_beneficiary_report_no_evaluations(self, mock_pdf_class):
        """Test generating beneficiary report without evaluations."""
        # Mock objects
        mock_user = Mock()
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        mock_beneficiary = Mock()
        mock_beneficiary.first_name = "Jane"
        mock_beneficiary.last_name = "Smith"
        mock_beneficiary.email = "jane@example.com"
        mock_beneficiary.status = "active"
        
        # No trainer
        mock_beneficiary.trainer = None
        
        evaluations = []
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_beneficiary_report(mock_beneficiary, evaluations, mock_user)
        
        # Verify no trainer info was added
        assert not any(call[0][0] == "Trainer Information" for call in mock_pdf.add_subtitle.call_args_list)
        
        # Verify no table was added
        mock_pdf.add_table.assert_not_called()
        
        # Verify "no evaluations" message was added
        mock_pdf.add_paragraph.assert_any_call("No evaluations available.")
        
        assert result == b"PDF content"
        

class TestGenerateReportPDF:
    """Test generate_report_pdf function."""
    
    @patch('app.utils.pdf_generator.PDFGenerator')
    @patch('datetime.datetime')
    def test_generate_report_pdf_with_data(self, mock_datetime, mock_pdf_class):
        """Test generating report PDF with data."""
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0)
        mock_datetime.datetime = datetime.datetime
        
        template_data = {
            'title': 'Test Report',
            'description': 'Test description',
            'generated_at': '2023-01-01 12:00:00',
            'generated_by': 'Test User',
            'report_type': 'Summary',
            'data': [
                {'col1': 'value1', 'col2': 'value2'},
                {'col1': 'value3', 'col2': 'value4'}
            ]
        }
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_report_pdf(template_data)
        
        # Verify PDF generator was created correctly
        mock_pdf_class.assert_called_with('Test Report')
        
        # Verify methods were called
        mock_pdf.add_title.assert_called_with('Test Report')
        mock_pdf.add_paragraph.assert_any_call('Test description')
        mock_pdf.add_subtitle.assert_any_call("Report Information")
        mock_pdf.add_subtitle.assert_any_call("Report Data")
        
        # Verify table was added
        mock_pdf.add_table.assert_called_once()
        table_data = mock_pdf.add_table.call_args[0][0]
        assert table_data[0] == ['col1', 'col2']
        assert table_data[1] == ['value1', 'value2']
        assert table_data[2] == ['value3', 'value4']
        
        assert result == b"PDF content"
        
    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_report_pdf_no_data(self, mock_pdf_class):
        """Test generating report PDF without data."""
        template_data = {
            'title': 'Empty Report',
            'data': []
        }
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_report_pdf(template_data)
        
        # Verify no table was added
        mock_pdf.add_table.assert_not_called()
        
        # Verify "no data" message was added
        mock_pdf.add_paragraph.assert_any_call("No data available for this report.")
        
        assert result == b"PDF content"
        
    @patch('app.utils.pdf_generator.PDFGenerator')
    def test_generate_report_pdf_defaults(self, mock_pdf_class):
        """Test generating report PDF with default values."""
        template_data = {}
        
        # Mock PDF generator instance
        mock_pdf = Mock()
        mock_pdf_class.return_value = mock_pdf
        mock_pdf.build.return_value = b"PDF content"
        
        # Call function
        result = generate_report_pdf(template_data)
        
        # Verify default title was used
        mock_pdf_class.assert_called_with('Report')
        
        # Verify default values in metadata
        calls = [str(call) for call in mock_pdf.add_paragraph.call_args_list]
        assert any('<b>Generated By:</b> System' in str(call) for call in calls)
        assert any('<b>Report Type:</b> General' in str(call) for call in calls)
        
        assert result == b"PDF content"