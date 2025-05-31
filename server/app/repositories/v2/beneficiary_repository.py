"""Concrete implementation of beneficiary repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import joinedload

from app.models import Beneficiary, Note, Document, Appointment
from app.repositories.v2.base_repository import BaseRepository
from app.repositories.v2.interfaces.beneficiary_repository_interface import IBeneficiaryRepository


class BeneficiaryRepository(BaseRepository[Beneficiary], IBeneficiaryRepository):
    """Beneficiary repository with concrete implementations."""
    
    def __init__(self, db_session):
        """Initialize beneficiary repository."""
        super().__init__(db_session, Beneficiary)
    
    def find_by_email(self, email: str) -> Optional[Beneficiary]:
        """Find beneficiary by email address."""
        return self.find_one_by(email=email)
    
    def find_by_phone(self, phone: str) -> Optional[Beneficiary]:
        """Find beneficiary by phone number."""
        return self.find_one_by(phone=phone)
    
    def find_by_national_id(self, national_id: str) -> Optional[Beneficiary]:
        """Find beneficiary by national ID."""
        return self.find_one_by(national_id=national_id)
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Beneficiary]:
        """Search beneficiaries with query and filters."""
        search_query = self.db.query(self.model_class)
        
        # Apply text search
        if query:
            search_filter = or_(
                self.model_class.name.ilike(f'%{query}%'),
                self.model_class.surname.ilike(f'%{query}%'),
                self.model_class.email.ilike(f'%{query}%'),
                self.model_class.phone.ilike(f'%{query}%'),
                self.model_class.national_id.ilike(f'%{query}%')
            )
            search_query = search_query.filter(search_filter)
        
        # Apply additional filters
        if filters:
            if 'status' in filters:
                search_query = search_query.filter(self.model_class.status == filters['status'])
            if 'city' in filters:
                search_query = search_query.filter(self.model_class.city == filters['city'])
            if 'program_id' in filters:
                search_query = search_query.filter(
                    self.model_class.programs.any(id=filters['program_id'])
                )
            if 'created_after' in filters:
                search_query = search_query.filter(
                    self.model_class.created_at >= filters['created_after']
                )
            if 'created_before' in filters:
                search_query = search_query.filter(
                    self.model_class.created_at <= filters['created_before']
                )
        
        return search_query.all()
    
    def get_active_beneficiaries(self) -> List[Beneficiary]:
        """Get all active beneficiaries."""
        return self.find_all_by(status='active')
    
    def get_inactive_beneficiaries(self) -> List[Beneficiary]:
        """Get all inactive beneficiaries."""
        return self.find_all_by(status='inactive')
    
    def get_beneficiaries_by_program(self, program_id: int) -> List[Beneficiary]:
        """Get beneficiaries enrolled in a specific program."""
        return self.db.query(self.model_class).filter(
            self.model_class.programs.any(id=program_id)
        ).all()
    
    def get_recently_updated(self, days: int = 7) -> List[Beneficiary]:
        """Get beneficiaries updated in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(self.model_class).filter(
            self.model_class.updated_at >= cutoff_date
        ).order_by(desc(self.model_class.updated_at)).all()
    
    def count_by_status(self) -> Dict[str, int]:
        """Count beneficiaries by status."""
        results = self.db.query(
            self.model_class.status,
            func.count(self.model_class.id)
        ).group_by(self.model_class.status).all()
        
        return {status: count for status, count in results}
    
    def count_by_city(self) -> Dict[str, int]:
        """Count beneficiaries by city."""
        results = self.db.query(
            self.model_class.city,
            func.count(self.model_class.id)
        ).group_by(self.model_class.city).all()
        
        return {city: count for city, count in results if city}
    
    # Note management
    def add_note(self, beneficiary_id: int, note_data: Dict[str, Any]) -> Note:
        """Add a note to a beneficiary."""
        note = Note(
            beneficiary_id=beneficiary_id,
            content=note_data['content'],
            created_by_id=note_data['created_by_id'],
            note_type=note_data.get('note_type', 'general'),
            is_private=note_data.get('is_private', False)
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note
    
    def get_notes(self, beneficiary_id: int, include_private: bool = False) -> List[Note]:
        """Get notes for a beneficiary."""
        query = self.db.query(Note).filter(
            Note.beneficiary_id == beneficiary_id
        )
        
        if not include_private:
            query = query.filter(Note.is_private == False)
        
        return query.order_by(desc(Note.created_at)).all()
    
    def update_note(self, note_id: int, content: str) -> Optional[Note]:
        """Update a beneficiary note."""
        note = self.db.query(Note).filter(
            Note.id == note_id
        ).first()
        
        if note:
            note.content = content
            note.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(note)
        
        return note
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a beneficiary note."""
        note = self.db.query(Note).filter(
            Note.id == note_id
        ).first()
        
        if note:
            self.db.delete(note)
            self.db.commit()
            return True
        
        return False
    
    # Document management
    def add_document(self, beneficiary_id: int, document_data: Dict[str, Any]) -> Document:
        """Add a document to a beneficiary."""
        document = Document(
            beneficiary_id=beneficiary_id,
            title=document_data['title'],
            file_path=document_data['file_path'],
            document_type=document_data.get('document_type', 'other'),
            uploaded_by_id=document_data['uploaded_by_id'],
            file_size=document_data.get('file_size', 0),
            mime_type=document_data.get('mime_type', 'application/octet-stream')
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_documents(self, beneficiary_id: int, document_type: Optional[str] = None) -> List[Document]:
        """Get documents for a beneficiary."""
        query = self.db.query(Document).filter(
            Document.beneficiary_id == beneficiary_id
        )
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        return query.order_by(desc(Document.created_at)).all()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a beneficiary document."""
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        
        return False
    
    # Appointment management
    def schedule_appointment(self, beneficiary_id: int, appointment_data: Dict[str, Any]) -> Appointment:
        """Schedule an appointment for a beneficiary."""
        appointment = Appointment(
            beneficiary_id=beneficiary_id,
            title=appointment_data['title'],
            scheduled_date=appointment_data['scheduled_date'],
            scheduled_time=appointment_data.get('scheduled_time'),
            duration_minutes=appointment_data.get('duration_minutes', 30),
            location=appointment_data.get('location'),
            notes=appointment_data.get('notes'),
            created_by_id=appointment_data['created_by_id'],
            status='scheduled'
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def get_appointments(self, beneficiary_id: int, include_past: bool = False) -> List[Appointment]:
        """Get appointments for a beneficiary."""
        query = self.db.query(Appointment).filter(
            Appointment.beneficiary_id == beneficiary_id
        )
        
        if not include_past:
            query = query.filter(Appointment.scheduled_date >= datetime.utcnow().date())
        
        return query.order_by(Appointment.scheduled_date, Appointment.scheduled_time).all()
    
    def update_appointment_status(self, appointment_id: int, status: str) -> Optional[Appointment]:
        """Update appointment status."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if appointment:
            appointment.status = status
            appointment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(appointment)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel an appointment."""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if appointment:
            appointment.status = 'cancelled'
            if reason:
                appointment.notes = f"{appointment.notes}\nCancellation reason: {reason}" if appointment.notes else f"Cancellation reason: {reason}"
            appointment.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False