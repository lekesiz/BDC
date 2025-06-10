"""Beneficiary service implementation with dependency injection."""
import os
import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.models import Beneficiary, Note, Document, Appointment, Program
from app.repositories.v2.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.repositories.v2.beneficiary_repository import BeneficiaryRepository
from app.services.v2.interfaces.beneficiary_service_interface import IBeneficiaryService
from app.utils.pdf_generator import PDFGenerator
from app.utils.cache import cache, generate_cache_key


class BeneficiaryServiceV2(IBeneficiaryService):
    """Beneficiary service with dependency injection."""
    
    def __init__(self, beneficiary_repository: Optional[IBeneficiaryRepository] = None,
                 db_session: Optional[Session] = None):
        """Initialize beneficiary service with dependencies."""
        self.beneficiary_repository = beneficiary_repository
        self.db_session = db_session
    
    def _get_repository(self) -> IBeneficiaryRepository:
        """Get beneficiary repository instance."""
        if self.beneficiary_repository:
            return self.beneficiary_repository
        
        # Fallback to creating repository with current session
        from app.extensions import db
        session = self.db_session or db.session
        return BeneficiaryRepository(session)
    
    def create_beneficiary(self, beneficiary_data: Dict[str, Any]) -> Beneficiary:
        """Create a new beneficiary."""
        repo = self._get_repository()
        
        # Check for duplicates
        if 'email' in beneficiary_data and beneficiary_data['email']:
            existing = repo.find_by_email(beneficiary_data['email'])
            if existing:
                raise ValueError(f"Beneficiary with email {beneficiary_data['email']} already exists")
        
        if 'national_id' in beneficiary_data and beneficiary_data['national_id']:
            existing = repo.find_by_national_id(beneficiary_data['national_id'])
            if existing:
                raise ValueError(f"Beneficiary with national ID {beneficiary_data['national_id']} already exists")
        
        # Create beneficiary
        beneficiary = Beneficiary(**beneficiary_data)
        created_beneficiary = repo.create(beneficiary)
        
        # Clear cache
        self._clear_cache()
        
        return created_beneficiary
    
    def get_beneficiary(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get beneficiary by ID."""
        # Try cache first
        cache_key = generate_cache_key('beneficiary', beneficiary_id)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        repo = self._get_repository()
        beneficiary = repo.find_by_id(beneficiary_id)
        
        if beneficiary:
            cache.set(cache_key, beneficiary, timeout=300)  # 5 minutes
        
        return beneficiary
    
    def update_beneficiary(self, beneficiary_id: int, update_data: Dict[str, Any]) -> Optional[Beneficiary]:
        """Update beneficiary information."""
        repo = self._get_repository()
        beneficiary = repo.find_by_id(beneficiary_id)
        
        if not beneficiary:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(beneficiary, key):
                setattr(beneficiary, key, value)
        
        updated_beneficiary = repo.update(beneficiary)
        
        # Clear cache
        cache_key = generate_cache_key('beneficiary', beneficiary_id)
        cache.delete(cache_key)
        self._clear_cache()
        
        return updated_beneficiary
    
    def delete_beneficiary(self, beneficiary_id: int) -> bool:
        """Delete a beneficiary."""
        repo = self._get_repository()
        result = repo.delete(beneficiary_id)
        
        if result:
            # Clear cache
            cache_key = generate_cache_key('beneficiary', beneficiary_id)
            cache.delete(cache_key)
            self._clear_cache()
        
        return result
    
    def search_beneficiaries(self, query: str, filters: Optional[Dict[str, Any]] = None,
                           page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search beneficiaries with pagination."""
        repo = self._get_repository()
        
        # Get all matching beneficiaries
        beneficiaries = repo.search(query, filters)
        
        # Manual pagination
        total = len(beneficiaries)
        start = (page - 1) * per_page
        end = start + per_page
        items = beneficiaries[start:end]
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_beneficiary_by_email(self, email: str) -> Optional[Beneficiary]:
        """Get beneficiary by email."""
        repo = self._get_repository()
        return repo.find_by_email(email)
    
    def get_beneficiary_by_national_id(self, national_id: str) -> Optional[Beneficiary]:
        """Get beneficiary by national ID."""
        repo = self._get_repository()
        return repo.find_by_national_id(national_id)
    
    def get_beneficiaries_by_program(self, program_id: int) -> List[Beneficiary]:
        """Get all beneficiaries in a program."""
        repo = self._get_repository()
        return repo.get_beneficiaries_by_program(program_id)
    
    def enroll_in_program(self, beneficiary_id: int, program_id: int) -> bool:
        """Enroll beneficiary in a program."""
        from app.extensions import db
        
        beneficiary = self.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return False
        
        # Get program
        program = db.session.query(Program).filter_by(id=program_id).first()
        if not program:
            return False
        
        # Check if already enrolled
        if program in beneficiary.programs:
            return True
        
        # Enroll
        beneficiary.programs.append(program)
        db.session.commit()
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def unenroll_from_program(self, beneficiary_id: int, program_id: int) -> bool:
        """Unenroll beneficiary from a program."""
        from app.extensions import db
        
        beneficiary = self.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return False
        
        # Get program
        program = db.session.query(Program).filter_by(id=program_id).first()
        if not program or program not in beneficiary.programs:
            return False
        
        # Unenroll
        beneficiary.programs.remove(program)
        db.session.commit()
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def get_beneficiary_statistics(self) -> Dict[str, Any]:
        """Get beneficiary statistics."""
        # Try cache first
        cache_key = generate_cache_key('beneficiary_stats')
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        repo = self._get_repository()
        
        stats = {
            'total': repo.count(),
            'by_status': repo.count_by_status(),
            'by_city': repo.count_by_city(),
            'active': len(repo.get_active_beneficiaries()),
            'inactive': len(repo.get_inactive_beneficiaries()),
            'recently_updated': len(repo.get_recently_updated(7))
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, timeout=600)
        
        return stats
    
    # Note management
    def add_note(self, beneficiary_id: int, note_content: str, note_type: str = 'general',
                 is_private: bool = False, created_by_id: int = None) -> Note:
        """Add a note to beneficiary."""
        repo = self._get_repository()
        
        note_data = {
            'content': note_content,
            'note_type': note_type,
            'is_private': is_private,
            'created_by_id': created_by_id or 1  # Default to system user
        }
        
        note = repo.add_note(beneficiary_id, note_data)
        
        # Clear cache
        self._clear_cache()
        
        return note
    
    def get_notes(self, beneficiary_id: int, include_private: bool = False) -> List[Note]:
        """Get beneficiary notes."""
        repo = self._get_repository()
        return repo.get_notes(beneficiary_id, include_private)
    
    def update_note(self, note_id: int, content: str) -> Optional[Note]:
        """Update a note."""
        repo = self._get_repository()
        note = repo.update_note(note_id, content)
        
        if note:
            self._clear_cache()
        
        return note
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        repo = self._get_repository()
        result = repo.delete_note(note_id)
        
        if result:
            self._clear_cache()
        
        return result
    
    # Document management
    def upload_document(self, beneficiary_id: int, file_data: Dict[str, Any]) -> Document:
        """Upload a document for beneficiary."""
        repo = self._get_repository()
        
        # Save file
        file = file_data['file']
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Create upload directory if not exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'beneficiary_documents', str(beneficiary_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Create document record
        document_data = {
            'title': file_data.get('title', filename),
            'file_path': file_path,
            'document_type': file_data.get('document_type', 'other'),
            'uploaded_by_id': file_data.get('uploaded_by_id', 1),
            'file_size': os.path.getsize(file_path),
            'mime_type': file.content_type
        }
        
        document = repo.add_document(beneficiary_id, document_data)
        
        # Clear cache
        self._clear_cache()
        
        return document
    
    def get_documents(self, beneficiary_id: int, document_type: Optional[str] = None) -> List[Document]:
        """Get beneficiary documents."""
        repo = self._get_repository()
        return repo.get_documents(beneficiary_id, document_type)
    
    def download_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Download a document."""
        from app.extensions import db
        
        document = db.session.query(Document).filter_by(id=document_id).first()
        if not document or not os.path.exists(document.file_path):
            return None
        
        with open(document.file_path, 'rb') as f:
            content = f.read()
        
        return {
            'content': content,
            'filename': os.path.basename(document.file_path),
            'mime_type': document.mime_type
        }
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document."""
        from app.extensions import db
        
        document = db.session.query(Document).filter_by(id=document_id).first()
        if not document:
            return False
        
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete record
        repo = self._get_repository()
        result = repo.delete_document(document_id)
        
        if result:
            self._clear_cache()
        
        return result
    
    # Appointment management
    def schedule_appointment(self, beneficiary_id: int, appointment_data: Dict[str, Any]) -> Appointment:
        """Schedule an appointment."""
        repo = self._get_repository()
        
        # Add created_by_id if not present
        if 'created_by_id' not in appointment_data:
            appointment_data['created_by_id'] = 1  # Default to system user
        
        appointment = repo.schedule_appointment(beneficiary_id, appointment_data)
        
        # Clear cache
        self._clear_cache()
        
        return appointment
    
    def get_appointments(self, beneficiary_id: int, include_past: bool = False) -> List[Appointment]:
        """Get beneficiary appointments."""
        repo = self._get_repository()
        return repo.get_appointments(beneficiary_id, include_past)
    
    def update_appointment(self, appointment_id: int, update_data: Dict[str, Any]) -> Optional[Appointment]:
        """Update an appointment."""
        from app.extensions import db
        
        appointment = db.session.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Clear cache
        self._clear_cache()
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel an appointment."""
        repo = self._get_repository()
        result = repo.cancel_appointment(appointment_id, reason)
        
        if result:
            self._clear_cache()
        
        return result
    
    def get_upcoming_appointments(self, days: int = 7) -> List[Appointment]:
        """Get upcoming appointments for all beneficiaries."""
        from app.extensions import db
        
        cutoff_date = datetime.utcnow().date() + timedelta(days=days)
        
        appointments = db.session.query(Appointment).filter(
            Appointment.scheduled_date >= datetime.utcnow().date(),
            Appointment.scheduled_date <= cutoff_date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).order_by(Appointment.scheduled_date, Appointment.scheduled_time).all()
        
        return appointments
    
    # Export functionality
    def export_beneficiary_data(self, beneficiary_id: int, format: str = 'pdf') -> bytes:
        """Export beneficiary data in specified format."""
        beneficiary = self.get_beneficiary(beneficiary_id)
        if not beneficiary:
            raise ValueError(f"Beneficiary {beneficiary_id} not found")
        
        if format == 'pdf':
            return self._export_beneficiary_pdf(beneficiary)
        elif format == 'csv':
            return self._export_beneficiary_csv(beneficiary)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def export_beneficiaries_list(self, filters: Optional[Dict[str, Any]] = None,
                                 format: str = 'csv') -> bytes:
        """Export list of beneficiaries."""
        repo = self._get_repository()
        beneficiaries = repo.search('', filters) if filters else repo.find_all()
        
        if format == 'csv':
            return self._export_beneficiaries_csv(beneficiaries)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_beneficiary_pdf(self, beneficiary: Beneficiary) -> bytes:
        """Export beneficiary data as PDF."""
        pdf = PDFGenerator(f"Beneficiary Profile: {beneficiary.name} {beneficiary.surname}", "BDC System")
        
        # Add beneficiary info
        pdf.add_heading("Personal Information")
        pdf.add_paragraph(f"Name: {beneficiary.name} {beneficiary.surname}")
        pdf.add_paragraph(f"Email: {beneficiary.email or 'N/A'}")
        pdf.add_paragraph(f"Phone: {beneficiary.phone or 'N/A'}")
        pdf.add_paragraph(f"National ID: {beneficiary.national_id or 'N/A'}")
        pdf.add_paragraph(f"Date of Birth: {beneficiary.date_of_birth or 'N/A'}")
        pdf.add_paragraph(f"City: {beneficiary.city or 'N/A'}")
        pdf.add_paragraph(f"Status: {beneficiary.status}")
        
        # Add programs
        if beneficiary.programs:
            pdf.add_heading("Enrolled Programs")
            for program in beneficiary.programs:
                pdf.add_paragraph(f"- {program.name}")
        
        # Add recent notes
        notes = self.get_notes(beneficiary.id, include_private=False)[:5]
        if notes:
            pdf.add_heading("Recent Notes")
            for note in notes:
                pdf.add_paragraph(f"{note.created_at.strftime('%Y-%m-%d')}: {note.content[:100]}...")
        
        # Add upcoming appointments
        appointments = self.get_appointments(beneficiary.id, include_past=False)[:5]
        if appointments:
            pdf.add_heading("Upcoming Appointments")
            for appointment in appointments:
                pdf.add_paragraph(f"{appointment.scheduled_date} - {appointment.title}")
        
        return pdf.generate()
    
    def _export_beneficiary_csv(self, beneficiary: Beneficiary) -> bytes:
        """Export beneficiary data as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Field', 'Value'])
        
        # Data
        writer.writerow(['ID', beneficiary.id])
        writer.writerow(['Name', f"{beneficiary.name} {beneficiary.surname}"])
        writer.writerow(['Email', beneficiary.email or ''])
        writer.writerow(['Phone', beneficiary.phone or ''])
        writer.writerow(['National ID', beneficiary.national_id or ''])
        writer.writerow(['Date of Birth', beneficiary.date_of_birth or ''])
        writer.writerow(['City', beneficiary.city or ''])
        writer.writerow(['Status', beneficiary.status])
        writer.writerow(['Created At', beneficiary.created_at])
        writer.writerow(['Updated At', beneficiary.updated_at])
        
        return output.getvalue().encode('utf-8')
    
    def _export_beneficiaries_csv(self, beneficiaries: List[Beneficiary]) -> bytes:
        """Export list of beneficiaries as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'National ID', 'City', 'Status', 'Created At'])
        
        # Data
        for b in beneficiaries:
            writer.writerow([
                b.id,
                f"{b.name} {b.surname}",
                b.email or '',
                b.phone or '',
                b.national_id or '',
                b.city or '',
                b.status,
                b.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return output.getvalue().encode('utf-8')
    
    def _clear_cache(self):
        """Clear relevant cache entries."""
        cache.delete_many(
            generate_cache_key('beneficiary_stats'),
            generate_cache_key('beneficiaries_list')
        )


# Backward compatibility aliases
BeneficiaryService = BeneficiaryServiceV2
NoteService = BeneficiaryServiceV2  # Assuming NoteService is part of BeneficiaryService
AppointmentService = BeneficiaryServiceV2  # Assuming AppointmentService is part of BeneficiaryService