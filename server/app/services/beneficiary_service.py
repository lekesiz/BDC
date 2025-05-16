"""Beneficiary service module."""

import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

from app.models import User, Beneficiary, Note, Appointment, Document
from app.extensions import db
from app.utils import clear_user_cache, clear_model_cache


class BeneficiaryService:
    """Beneficiary service."""
    
    @staticmethod
    def get_beneficiaries(tenant_id=None, trainer_id=None, status=None, query=None, page=1, per_page=10, sort_by=None, sort_dir=None):
        """
        Get beneficiaries with optional filtering.
        
        Args:
            tenant_id (int, optional): Filter by tenant ID.
            trainer_id (int, optional): Filter by trainer ID.
            status (str, optional): Filter by status.
            query (str, optional): Search query for name or email.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (beneficiaries, total, pages)
        """
        # Build query
        beneficiary_query = Beneficiary.query
        
        # Apply filters
        if tenant_id:
            beneficiary_query = beneficiary_query.filter_by(tenant_id=tenant_id)
        
        if trainer_id:
            beneficiary_query = beneficiary_query.filter_by(trainer_id=trainer_id)
        
        if status:
            beneficiary_query = beneficiary_query.filter_by(status=status)
        
        if query:
            # Join with User table to search in first_name, last_name and email
            # Be explicit about which relationship to join
            from sqlalchemy.orm import aliased
            beneficiary_user = aliased(User)
            beneficiary_query = beneficiary_query.join(
                beneficiary_user, 
                Beneficiary.user_id == beneficiary_user.id
            ).filter(
                (beneficiary_user.first_name.ilike(f'%{query}%')) |
                (beneficiary_user.last_name.ilike(f'%{query}%')) |
                (beneficiary_user.email.ilike(f'%{query}%'))
            )
        
        # Apply sorting
        if sort_by:
            valid_sort_fields = ['created_at', 'updated_at', 'first_name', 'last_name', 'email']
            if sort_by in valid_sort_fields:
                # Handle user fields separately
                if sort_by in ['first_name', 'last_name', 'email']:
                    if 'beneficiary_user' not in locals():
                        from sqlalchemy.orm import aliased
                        beneficiary_user = aliased(User)
                        beneficiary_query = beneficiary_query.join(
                            beneficiary_user,
                            Beneficiary.user_id == beneficiary_user.id
                        )
                    sort_column = getattr(beneficiary_user, sort_by)
                else:
                    sort_column = getattr(Beneficiary, sort_by)
                
                if sort_dir == 'desc':
                    beneficiary_query = beneficiary_query.order_by(sort_column.desc())
                else:
                    beneficiary_query = beneficiary_query.order_by(sort_column.asc())
        else:
            # Default sorting
            beneficiary_query = beneficiary_query.order_by(Beneficiary.created_at.desc())
        
        # Paginate results
        pagination = beneficiary_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_beneficiary(beneficiary_id):
        """
        Get a beneficiary by ID.
        
        Args:
            beneficiary_id (int): Beneficiary ID.
        
        Returns:
            Beneficiary: The beneficiary or None if not found.
        """
        return Beneficiary.query.get(beneficiary_id)
    
    @staticmethod
    def create_beneficiary(user_data, beneficiary_data):
        """
        Create a new beneficiary with a user account.
        
        Args:
            user_data (dict): User data.
            beneficiary_data (dict): Beneficiary data.
        
        Returns:
            Beneficiary: The created beneficiary or None if creation fails.
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                # Check if user already has a beneficiary profile
                existing_beneficiary = Beneficiary.query.filter_by(user_id=existing_user.id).first()
                if existing_beneficiary:
                    current_app.logger.error(f"User {user_data['email']} already has a beneficiary profile")
                    return None
                
                # Use existing user
                user = existing_user
                # Update user info if provided
                if user_data.get('first_name'):
                    user.first_name = user_data['first_name']
                if user_data.get('last_name'):
                    user.last_name = user_data['last_name']
            else:
                # Create new user
                user = User(
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role='student',
                    is_active=True
                )
                user.password = user_data['password']
                
                # Set tenant_id directly instead of relationship
                if beneficiary_data.get('tenant_id'):
                    user.tenant_id = beneficiary_data['tenant_id']
                
                db.session.add(user)
                db.session.flush()  # Get user ID without committing
            
            # Create beneficiary
            beneficiary = Beneficiary(
                user_id=user.id,
                trainer_id=beneficiary_data.get('trainer_id'),
                tenant_id=beneficiary_data['tenant_id'],
                gender=beneficiary_data.get('gender'),
                birth_date=beneficiary_data.get('birth_date'),
                phone=beneficiary_data.get('phone'),
                address=beneficiary_data.get('address'),
                city=beneficiary_data.get('city'),
                postal_code=beneficiary_data.get('postal_code'),
                state=beneficiary_data.get('state'),
                country=beneficiary_data.get('country'),
                nationality=beneficiary_data.get('nationality'),
                native_language=beneficiary_data.get('native_language'),
                profession=beneficiary_data.get('profession'),
                company=beneficiary_data.get('company'),
                company_size=beneficiary_data.get('company_size'),
                years_of_experience=beneficiary_data.get('years_of_experience'),
                education_level=beneficiary_data.get('education_level'),
                category=beneficiary_data.get('category'),
                bio=beneficiary_data.get('bio'),
                goals=beneficiary_data.get('goals'),
                notes=beneficiary_data.get('notes'),
                referral_source=beneficiary_data.get('referral_source'),
                custom_fields=beneficiary_data.get('custom_fields') if beneficiary_data.get('custom_fields') else None,
                status=beneficiary_data.get('status', 'active'),
                is_active=True
            )
            
            db.session.add(beneficiary)
            db.session.commit()
            
            # Clear cache
            clear_model_cache('beneficiaries')
            
            return beneficiary
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating beneficiary: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def update_beneficiary(beneficiary_id, data):
        """
        Update a beneficiary.
        
        Args:
            beneficiary_id (int): Beneficiary ID.
            data (dict): Data to update.
        
        Returns:
            Beneficiary: The updated beneficiary or None if update fails.
        """
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            
            if not beneficiary:
                return None
            
            # Separate user fields from beneficiary fields
            user_fields = ['first_name', 'last_name', 'email']
            user_data = {}
            beneficiary_data = {}
            
            for key, value in data.items():
                if key in user_fields:
                    user_data[key] = value
                else:
                    beneficiary_data[key] = value
            
            # Update user if needed
            if user_data and beneficiary.user:
                for key, value in user_data.items():
                    if hasattr(beneficiary.user, key):
                        setattr(beneficiary.user, key, value)
                beneficiary.user.updated_at = datetime.now(timezone.utc)
            
            # Update beneficiary attributes
            for key, value in beneficiary_data.items():
                if hasattr(beneficiary, key):
                    # Check if it's a property without a setter
                    prop = getattr(type(beneficiary), key, None)
                    if prop is None or (hasattr(prop, 'fset') and prop.fset is not None):
                        # It's either not a property or a property with a setter
                        if key == 'custom_fields' and value is not None:
                            setattr(beneficiary, key, value)
                        else:
                            setattr(beneficiary, key, value)
            
            beneficiary.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('beneficiaries')
            
            return beneficiary
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating beneficiary: {str(e)}")
            return None
    
    @staticmethod
    def delete_beneficiary(beneficiary_id):
        """
        Delete a beneficiary.
        
        Args:
            beneficiary_id (int): Beneficiary ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            
            if not beneficiary:
                return False
            
            # Delete associated data
            Note.query.filter_by(beneficiary_id=beneficiary_id).delete()
            Appointment.query.filter_by(beneficiary_id=beneficiary_id).delete()
            
            # Delete documents
            documents = Document.query.filter_by(beneficiary_id=beneficiary_id).all()
            for document in documents:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            Document.query.filter_by(beneficiary_id=beneficiary_id).delete()
            
            # Delete beneficiary
            db.session.delete(beneficiary)
            
            # The associated user remains, but could be deactivated if needed
            user = User.query.get(beneficiary.user_id)
            if user:
                user.is_active = False
                user.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('beneficiaries')
            
            return True
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting beneficiary: {str(e)}")
            return False
    
    @staticmethod
    def assign_trainer(beneficiary_id, trainer_id):
        """
        Assign a trainer to a beneficiary.
        
        Args:
            beneficiary_id (int): Beneficiary ID.
            trainer_id (int): Trainer ID.
        
        Returns:
            Beneficiary: The updated beneficiary or None if assign fails.
        """
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            
            if not beneficiary:
                return None
            
            # Verify trainer exists and has appropriate role
            if trainer_id:
                trainer = User.query.get(trainer_id)
                if not trainer or trainer.role not in ['trainer', 'super_admin', 'tenant_admin']:
                    return None
            
            beneficiary.trainer_id = trainer_id
            beneficiary.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('beneficiaries')
            
            return beneficiary
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error assigning trainer: {str(e)}")
            return None


class NoteService:
    """Note service."""
    
    @staticmethod
    def get_notes(beneficiary_id, user_id=None, type=None, is_private=None, page=1, per_page=10):
        """
        Get notes for a beneficiary.
        
        Args:
            beneficiary_id (int): Beneficiary ID.
            user_id (int, optional): Filter by user ID.
            type (str, optional): Filter by type.
            is_private (bool, optional): Filter by is_private.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (notes, total, pages)
        """
        # Build query
        note_query = Note.query.filter_by(beneficiary_id=beneficiary_id)
        
        # Apply filters
        if user_id:
            note_query = note_query.filter_by(user_id=user_id)
        
        if type:
            note_query = note_query.filter_by(type=type)
        
        if is_private is not None:
            note_query = note_query.filter_by(is_private=is_private)
        
        # Order by created_at descending
        note_query = note_query.order_by(Note.created_at.desc())
        
        # Paginate results
        pagination = note_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_note(note_id):
        """
        Get a note by ID.
        
        Args:
            note_id (int): Note ID.
        
        Returns:
            Note: The note or None if not found.
        """
        return Note.query.get(note_id)
    
    @staticmethod
    def create_note(user_id, data):
        """
        Create a new note.
        
        Args:
            user_id (int): User ID.
            data (dict): Note data.
        
        Returns:
            Note: The created note or None if creation fails.
        """
        try:
            note = Note(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                content=data['content'],
                type=data.get('type', 'general'),
                is_private=data.get('is_private', False)
            )
            
            db.session.add(note)
            db.session.commit()
            
            return note
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating note: {str(e)}")
            return None
    
    @staticmethod
    def update_note(note_id, data):
        """
        Update a note.
        
        Args:
            note_id (int): Note ID.
            data (dict): Data to update.
        
        Returns:
            Note: The updated note or None if update fails.
        """
        try:
            note = Note.query.get(note_id)
            
            if not note:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(note, key):
                    setattr(note, key, value)
            
            note.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return note
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating note: {str(e)}")
            return None
    
    @staticmethod
    def delete_note(note_id):
        """
        Delete a note.
        
        Args:
            note_id (int): Note ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            note = Note.query.get(note_id)
            
            if not note:
                return False
            
            db.session.delete(note)
            db.session.commit()
            
            return True
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting note: {str(e)}")
            return False


class AppointmentService:
    """Appointment service."""
    
    @staticmethod
    def get_appointments(user_id=None, beneficiary_id=None, status=None, 
                        start_date=None, end_date=None, page=1, per_page=10):
        """
        Get appointments with optional filtering.
        
        Args:
            user_id (int, optional): Filter by user ID.
            beneficiary_id (int, optional): Filter by beneficiary ID.
            status (str, optional): Filter by status.
            start_date (datetime, optional): Filter by start date.
            end_date (datetime, optional): Filter by end date.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (appointments, total, pages)
        """
        # Build query
        appointment_query = Appointment.query
        
        # Apply filters
        if user_id:
            appointment_query = appointment_query.filter_by(user_id=user_id)
        
        if beneficiary_id:
            appointment_query = appointment_query.filter_by(beneficiary_id=beneficiary_id)
        
        if status:
            appointment_query = appointment_query.filter_by(status=status)
        
        if start_date:
            appointment_query = appointment_query.filter(Appointment.start_time >= start_date)
        
        if end_date:
            appointment_query = appointment_query.filter(Appointment.start_time <= end_date)
        
        # Order by start_time ascending
        appointment_query = appointment_query.order_by(Appointment.start_time.asc())
        
        # Paginate results
        pagination = appointment_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_appointment(appointment_id):
        """
        Get an appointment by ID.
        
        Args:
            appointment_id (int): Appointment ID.
        
        Returns:
            Appointment: The appointment or None if not found.
        """
        return Appointment.query.get(appointment_id)
    
    @staticmethod
    def create_appointment(user_id, data):
        """
        Create a new appointment.
        
        Args:
            user_id (int): User ID.
            data (dict): Appointment data.
        
        Returns:
            Appointment: The created appointment or None if creation fails.
        """
        try:
            appointment = Appointment(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                title=data['title'],
                description=data.get('description'),
                start_time=data['start_time'],
                end_time=data['end_time'],
                location=data.get('location', 'Online'),
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return appointment
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating appointment: {str(e)}")
            return None
    
    @staticmethod
    def update_appointment(appointment_id, data):
        """
        Update an appointment.
        
        Args:
            appointment_id (int): Appointment ID.
            data (dict): Data to update.
        
        Returns:
            Appointment: The updated appointment or None if update fails.
        """
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(appointment, key):
                    setattr(appointment, key, value)
            
            appointment.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return appointment
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating appointment: {str(e)}")
            return None
    
    @staticmethod
    def delete_appointment(appointment_id):
        """
        Delete an appointment.
        
        Args:
            appointment_id (int): Appointment ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            appointment = Appointment.query.get(appointment_id)
            
            if not appointment:
                return False
            
            db.session.delete(appointment)
            db.session.commit()
            
            return True
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting appointment: {str(e)}")
            return False


class DocumentService:
    """Document service."""
    
    @staticmethod
    def get_documents(beneficiary_id=None, user_id=None, page=1, per_page=10):
        """
        Get documents with optional filtering.
        
        Args:
            beneficiary_id (int, optional): Filter by beneficiary ID.
            user_id (int, optional): Filter by user ID.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (documents, total, pages)
        """
        # Build query
        document_query = Document.query
        
        # Apply filters
        if beneficiary_id:
            document_query = document_query.filter_by(beneficiary_id=beneficiary_id)
        
        if user_id:
            document_query = document_query.filter_by(user_id=user_id)
        
        # Order by created_at descending
        document_query = document_query.order_by(Document.created_at.desc())
        
        # Paginate results
        pagination = document_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_document(document_id):
        """
        Get a document by ID.
        
        Args:
            document_id (int): Document ID.
        
        Returns:
            Document: The document or None if not found.
        """
        return Document.query.get(document_id)
    
    @staticmethod
    def create_document(user_id, file, data):
        """
        Create a new document.
        
        Args:
            user_id (int): User ID.
            file (FileStorage): Uploaded file.
            data (dict): Document data.
        
        Returns:
            Document: The created document or None if creation fails.
        """
        try:
            # Generate a secure filename with a UUID to avoid collisions
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            
            # Get file extension
            _, file_extension = os.path.splitext(original_filename)
            file_type = file_extension[1:].lower() if file_extension else 'unknown'
            
            # Save file
            file_path = os.path.join('documents', filename)
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
            
            # Ensure the directory exists
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            
            file.save(os.path.join(full_path, filename))
            
            # Create document record
            document = Document(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                title=data['title'],
                description=data.get('description'),
                file_path=file_path,
                file_type=file_type,
                file_size=os.path.getsize(os.path.join(full_path, filename)),
                is_private=data.get('is_private', False)
            )
            
            db.session.add(document)
            db.session.commit()
            
            return document
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating document: {str(e)}")
            return None
    
    @staticmethod
    def update_document(document_id, data):
        """
        Update a document.
        
        Args:
            document_id (int): Document ID.
            data (dict): Data to update.
        
        Returns:
            Document: The updated document or None if update fails.
        """
        try:
            document = Document.query.get(document_id)
            
            if not document:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            document.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return document
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating document: {str(e)}")
            return None
    
    @staticmethod
    def delete_document(document_id):
        """
        Delete a document.
        
        Args:
            document_id (int): Document ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            document = Document.query.get(document_id)
            
            if not document:
                return False
            
            # Delete file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete document record
            db.session.delete(document)
            db.session.commit()
            
            return True
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting document: {str(e)}")
            return False