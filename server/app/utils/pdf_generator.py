"""PDF Generator utility using ReportLab."""

import os
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from flask import current_app


class PDFGenerator:
    """Class for generating PDF documents."""
    
    def __init__(self, title, author="BDC System"):
        """Initialize the PDF generator."""
        self.title = title
        self.author = author
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=title,
            author=author
        )
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.elements = []
        
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Override existing styles by modifying them directly
        self.styles['Heading1'].fontSize = 16
        self.styles['Heading1'].spaceAfter = 12
        
        self.styles['Heading2'].fontSize = 14
        self.styles['Heading2'].spaceAfter = 10
        self.styles['Heading2'].spaceBefore = 10
        
        self.styles['Heading3'].fontSize = 12
        self.styles['Heading3'].spaceAfter = 8
        self.styles['Heading3'].spaceBefore = 8
        
        self.styles['Normal'].fontSize = 10
        self.styles['Normal'].spaceAfter = 6
        
        self.styles['Italic'].fontSize = 10
        self.styles['Italic'].spaceAfter = 6
        
        # Add new Bold style (doesn't exist in base styles)
        self.styles.add(ParagraphStyle(
            name='Bold',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
    
    def add_title(self, text):
        """Add title to the document."""
        self.elements.append(Paragraph(text, self.styles['Heading1']))
        self.elements.append(Spacer(1, 0.5*cm))
    
    def add_subtitle(self, text):
        """Add subtitle to the document."""
        self.elements.append(Paragraph(text, self.styles['Heading2']))
        self.elements.append(Spacer(1, 0.3*cm))
    
    def add_heading(self, text):
        """Add heading to the document."""
        self.elements.append(Paragraph(text, self.styles['Heading3']))
        self.elements.append(Spacer(1, 0.2*cm))
    
    def add_paragraph(self, text):
        """Add paragraph to the document."""
        self.elements.append(Paragraph(text, self.styles['Normal']))
        self.elements.append(Spacer(1, 0.2*cm))
    
    def add_bold_text(self, text):
        """Add bold text to the document."""
        self.elements.append(Paragraph(text, self.styles['Bold']))
    
    def add_italic_text(self, text):
        """Add italic text to the document."""
        self.elements.append(Paragraph(text, self.styles['Italic']))
    
    def add_spacer(self, height=0.5):
        """Add spacer to the document."""
        self.elements.append(Spacer(1, height*cm))
    
    def add_table(self, data, col_widths=None, style=None):
        """Add table to the document."""
        if not style:
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ])
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(style)
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.5*cm))
    
    def add_image(self, image_path, width=None, height=None):
        """Add image to the document."""
        if not os.path.exists(image_path):
            return
        
        img = Image(image_path)
        if width:
            img.drawWidth = width
        if height:
            img.drawHeight = height
        self.elements.append(img)
        self.elements.append(Spacer(1, 0.3*cm))
    
    def add_page_break(self):
        """Add page break to the document."""
        self.elements.append(Spacer(1, A4[1]))
    
    def add_footer(self):
        """Add a standard footer to the document."""
        def add_footer_content(canvas, doc):
            canvas.saveState()
            # Draw footer line
            canvas.setStrokeColor(colors.grey)
            canvas.line(2*cm, 1.5*cm, A4[0]-2*cm, 1.5*cm)
            # Add footer text
            canvas.setFont('Helvetica', 8)
            canvas.drawString(2*cm, 1*cm, f"Generated by BDC - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            canvas.drawRightString(A4[0]-2*cm, 1*cm, f"Page {doc.page}")
            canvas.restoreState()
        
        return add_footer_content
    
    def build(self):
        """Build the PDF document."""
        self.doc.build(self.elements, onFirstPage=self.add_footer(), onLaterPages=self.add_footer())
        pdf_content = self.buffer.getvalue()
        self.buffer.close()
        return pdf_content


def generate_evaluation_report(evaluation, user, beneficiary):
    """Generate a report PDF for an evaluation."""
    pdf = PDFGenerator(f"Evaluation Report - {beneficiary.first_name} {beneficiary.last_name}")
    
    # Add title
    pdf.add_title(f"Evaluation Report")
    
    # Add beneficiary information
    pdf.add_subtitle("Beneficiary Information")
    pdf.add_paragraph(f"<b>Name:</b> {beneficiary.first_name} {beneficiary.last_name}")
    pdf.add_paragraph(f"<b>Email:</b> {beneficiary.email}")
    pdf.add_paragraph(f"<b>Status:</b> {beneficiary.status}")
    pdf.add_spacer()
    
    # Add evaluation details
    pdf.add_subtitle("Evaluation Details")
    pdf.add_paragraph(f"<b>Title:</b> {evaluation.title}")
    pdf.add_paragraph(f"<b>Date:</b> {evaluation.date_created.strftime('%Y-%m-%d')}")
    pdf.add_paragraph(f"<b>Status:</b> {evaluation.status}")
    if evaluation.score:
        pdf.add_paragraph(f"<b>Score:</b> {evaluation.score}%")
    pdf.add_spacer()
    
    # Add question and answers
    pdf.add_subtitle("Responses")
    
    # Display each question and answer
    for i, question in enumerate(evaluation.questions):
        pdf.add_heading(f"Question {i+1}: {question.text}")
        if hasattr(question, 'answer') and question.answer:
            pdf.add_paragraph(f"<b>Answer:</b> {question.answer.text}")
            if hasattr(question.answer, 'score') and question.answer.score is not None:
                pdf.add_paragraph(f"<b>Score:</b> {question.answer.score}")
        else:
            pdf.add_italic_text("No answer provided")
        pdf.add_spacer()
    
    # Add summary and recommendations if available
    if hasattr(evaluation, 'summary') and evaluation.summary:
        pdf.add_subtitle("Summary")
        pdf.add_paragraph(evaluation.summary)
        pdf.add_spacer()
    
    if hasattr(evaluation, 'recommendations') and evaluation.recommendations:
        pdf.add_subtitle("Recommendations")
        pdf.add_paragraph(evaluation.recommendations)
    
    # Add signature
    pdf.add_spacer()
    pdf.add_paragraph(f"Report generated by: {user.first_name} {user.last_name}")
    pdf.add_paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # Build the PDF
    return pdf.build()


def generate_beneficiary_report(beneficiary, evaluations, user):
    """Generate a comprehensive report for a beneficiary."""
    pdf = PDFGenerator(f"Beneficiary Report - {beneficiary.first_name} {beneficiary.last_name}")
    
    # Add title
    pdf.add_title(f"Beneficiary Progress Report")
    
    # Add beneficiary information
    pdf.add_subtitle("Beneficiary Information")
    pdf.add_paragraph(f"<b>Name:</b> {beneficiary.first_name} {beneficiary.last_name}")
    pdf.add_paragraph(f"<b>Email:</b> {beneficiary.email}")
    pdf.add_paragraph(f"<b>Status:</b> {beneficiary.status}")
    pdf.add_spacer()
    
    # Add trainer information if available
    if hasattr(beneficiary, 'trainer') and beneficiary.trainer:
        pdf.add_subtitle("Trainer Information")
        pdf.add_paragraph(f"<b>Name:</b> {beneficiary.trainer.first_name} {beneficiary.trainer.last_name}")
        pdf.add_paragraph(f"<b>Email:</b> {beneficiary.trainer.email}")
        pdf.add_spacer()
    
    # Add evaluations summary
    pdf.add_subtitle("Evaluations Summary")
    
    if evaluations:
        # Create table data
        data = [['Title', 'Date', 'Status', 'Score']]
        for eval in evaluations:
            data.append([
                eval.title,
                eval.date_created.strftime('%Y-%m-%d'),
                eval.status,
                f"{eval.score}%" if eval.score else "N/A"
            ])
        pdf.add_table(data)
        
        # Add overall progress
        completed_evals = [e for e in evaluations if e.status == 'completed']
        if completed_evals:
            avg_score = sum(e.score for e in completed_evals if e.score) / len(completed_evals)
            pdf.add_paragraph(f"<b>Overall Progress:</b> {len(completed_evals)}/{len(evaluations)} evaluations completed")
            pdf.add_paragraph(f"<b>Average Score:</b> {avg_score:.1f}%")
    else:
        pdf.add_paragraph("No evaluations available.")
    
    # Add summary and recommendations if available
    if hasattr(beneficiary, 'summary') and beneficiary.summary:
        pdf.add_subtitle("Summary")
        pdf.add_paragraph(beneficiary.summary)
    
    if hasattr(beneficiary, 'recommendations') and beneficiary.recommendations:
        pdf.add_subtitle("Recommendations")
        pdf.add_paragraph(beneficiary.recommendations)
    
    # Add signature
    pdf.add_spacer()
    pdf.add_paragraph(f"Report generated by: {user.first_name} {user.last_name}")
    pdf.add_paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # Build the PDF
    return pdf.build()


def generate_report_pdf(template_data):
    """Generate a report PDF from template data."""
    pdf = PDFGenerator(template_data.get('title', 'Report'))
    
    # Add title
    pdf.add_title(template_data.get('title', 'Report'))
    
    # Add description if available
    if template_data.get('description'):
        pdf.add_paragraph(template_data.get('description'))
        pdf.add_spacer()
    
    # Add metadata
    pdf.add_subtitle("Report Information")
    pdf.add_paragraph(f"<b>Generated At:</b> {template_data.get('generated_at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    pdf.add_paragraph(f"<b>Generated By:</b> {template_data.get('generated_by', 'System')}")
    pdf.add_paragraph(f"<b>Report Type:</b> {template_data.get('report_type', 'General')}")
    pdf.add_spacer()
    
    # Add data table
    data = template_data.get('data', [])
    if data:
        pdf.add_subtitle("Report Data")
        # Create table data
        headers = list(data[0].keys())
        table_data = [headers]
        
        for row in data:
            table_data.append([str(row.get(header, '')) for header in headers])
        
        # Calculate column widths based on content
        col_widths = []
        max_width = (A4[0] - 4*cm) / len(headers)  # Total available width divided by columns
        
        for i in range(len(headers)):
            # Get max content length for this column
            max_len = len(headers[i])
            for row in data:
                content = str(row.get(headers[i], ''))
                if len(content) > max_len:
                    max_len = len(content)
            
            # Calculate width (proportional to content, but not exceeding max_width)
            width = min(max_len * 0.15 * cm, max_width)
            col_widths.append(width)
        
        # Normalize widths to fit page
        total_width = sum(col_widths)
        if total_width > (A4[0] - 4*cm):
            factor = (A4[0] - 4*cm) / total_width
            col_widths = [w * factor for w in col_widths]
        
        # Add table
        pdf.add_table(table_data, col_widths=col_widths)
    else:
        pdf.add_paragraph("No data available for this report.")
    
    # Add footer info
    pdf.add_spacer()
    pdf.add_paragraph(f"<i>Total Records: {len(data)}</i>")
    
    # Build the PDF
    return pdf.build()