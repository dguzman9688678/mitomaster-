"""
MitoAI Platform - Enhanced Database Models
Creator: Daniel Guzman
Contact: guzman.daniel@outlook.com
Copyright: 2025 Daniel Guzman - All Rights Reserved

NO ONE IS AUTHORIZED TO ALTER THIS SOFTWARE UNLESS AUTHORIZED BY DANIEL GUZMAN

Complete database models for enterprise web application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin
from datetime import datetime, timedelta
import uuid
import json
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID, JSONB
from enum import Enum

db = SQLAlchemy()

class SubscriptionTier(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"

class ProjectStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class APIKeyStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"

class User(db.Model, UserMixin):
    """Enhanced user model with subscription and enterprise features"""
    
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    # Subscription information
    subscription_tier = db.Column(db.Enum(SubscriptionTier), default=SubscriptionTier.BASIC)
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime)
    monthly_fee = db.Column(db.Decimal(10, 2), default=29.00)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    
    # Usage tracking
    total_requests = db.Column(db.Integer, default=0)
    monthly_requests = db.Column(db.Integer, default=0)
    last_request = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set user password with secure hashing"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_usage_limits(self):
        """Get usage limits based on subscription tier"""
        limits = {
            SubscriptionTier.BASIC: {
                'monthly_requests': 1000,
                'concurrent_projects': 3,
                'api_keys': 2,
                'storage_gb': 1
            },
            SubscriptionTier.PROFESSIONAL: {
                'monthly_requests': 10000,
                'concurrent_projects': 10,
                'api_keys': 10,
                'storage_gb': 10
            },
            SubscriptionTier.ENTERPRISE: {
                'monthly_requests': 100000,
                'concurrent_projects': 50,
                'api_keys': 50,
                'storage_gb': 100
            },
            SubscriptionTier.UNLIMITED: {
                'monthly_requests': -1,  # Unlimited
                'concurrent_projects': -1,
                'api_keys': -1,
                'storage_gb': 1000
            }
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.BASIC])
    
    def can_make_request(self):
        """Check if user can make additional API requests"""
        limits = self.get_usage_limits()
        if limits['monthly_requests'] == -1:  # Unlimited
            return True
        return self.monthly_requests < limits['monthly_requests']
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'subscription_tier': self.subscription_tier.value,
            'monthly_fee': float(self.monthly_fee),
            'total_requests': self.total_requests,
            'monthly_requests': self.monthly_requests,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class APIKey(db.Model):
    """API key management for multi-model access"""
    
    __tablename__ = 'api_keys'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    key_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    key_prefix = db.Column(db.String(20), nullable=False)  # For display purposes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Access control
    business_models = db.Column(JSONB)  # List of allowed business models
    access_level = db.Column(db.Enum(SubscriptionTier), nullable=False)
    status = db.Column(db.Enum(APIKeyStatus), default=APIKeyStatus.ACTIVE)
    
    # Usage tracking
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    # Rate limiting
    rate_limit_per_minute = db.Column(db.Integer, default=60)
    rate_limit_per_hour = db.Column(db.Integer, default=1000)
    rate_limit_per_day = db.Column(db.Integer, default=10000)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    usage_logs = db.relationship('UsageLog', backref='api_key', lazy='dynamic')
    
    @staticmethod
    def generate_key():
        """Generate a new API key"""
        import secrets
        key = f"mitoai_{secrets.token_urlsafe(32)}"
        key_hash = generate_password_hash(key)
        key_prefix = key[:16] + "..."
        return key, key_hash, key_prefix
    
    def check_key(self, key):
        """Verify API key"""
        return check_password_hash(self.key_hash, key)
    
    def to_dict(self):
        """Convert API key to dictionary for responses"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'key_prefix': self.key_prefix,
            'business_models': self.business_models,
            'access_level': self.access_level.value,
            'status': self.status.value,
            'total_requests': self.total_requests,
            'success_rate': (self.successful_requests / max(self.total_requests, 1)) * 100,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class Project(db.Model):
    """Project management for AI-generated content and business plans"""
    
    __tablename__ = 'projects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Project classification
    project_type = db.Column(db.String(50), nullable=False)  # content, business_plan, presentation
    industry = db.Column(db.String(50))
    business_model = db.Column(db.String(100))  # Which AI model is managing this
    
    # Project status and progress
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    progress_percentage = db.Column(db.Integer, default=0)
    current_phase = db.Column(db.String(100))
    
    # Project data and settings
    project_data = db.Column(JSONB)  # Flexible project configuration
    generated_content = db.Column(JSONB)  # Store generated content
    metadata = db.Column(JSONB)  # Additional project metadata
    
    # Timeline and budget
    estimated_completion = db.Column(db.DateTime)
    actual_completion = db.Column(db.DateTime)
    budget_estimate = db.Column(db.Decimal(12, 2))
    actual_cost = db.Column(db.Decimal(12, 2))
    
    # Collaboration
    collaborators = db.Column(JSONB)  # List of user IDs with access
    sharing_settings = db.Column(JSONB)  # Privacy and sharing configuration
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('ProjectTask', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    files = db.relationship('ProjectFile', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type,
            'industry': self.industry,
            'business_model': self.business_model,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'current_phase': self.current_phase,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'budget_estimate': float(self.budget_estimate) if self.budget_estimate else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProjectTask(db.Model):
    """Individual tasks within projects"""
    
    __tablename__ = 'project_tasks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Task details
    task_type = db.Column(db.String(50))  # research, content_generation, analysis, etc.
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, blocked
    
    # Task data
    input_data = db.Column(JSONB)  # Task parameters and inputs
    output_data = db.Column(JSONB)  # Task results and outputs
    ai_model_used = db.Column(db.String(100))  # Which AI model processed this task
    
    # Timeline
    estimated_duration = db.Column(db.Integer)  # Minutes
    actual_duration = db.Column(db.Integer)  # Minutes
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectFile(db.Model):
    """Files associated with projects"""
    
    __tablename__ = 'project_files'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # document, image, audio, video, data
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.BigInteger)
    
    # Storage information
    storage_path = db.Column(db.String(500))
    storage_provider = db.Column(db.String(50), default='local')  # local, s3, gcs
    public_url = db.Column(db.String(500))
    
    # File metadata
    file_metadata = db.Column(JSONB)  # Additional file-specific data
    processing_status = db.Column(db.String(20), default='uploaded')  # uploaded, processing, ready, error
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    access_permissions = db.Column(JSONB)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UsageLog(db.Model):
    """Detailed usage logging for analytics and billing"""
    
    __tablename__ = 'usage_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    api_key_id = db.Column(UUID(as_uuid=True), db.ForeignKey('api_keys.id'))
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    
    # Request details
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    business_model = db.Column(db.String(100))
    
    # Request data
    request_data = db.Column(JSONB)  # Sanitized request parameters
    response_data = db.Column(JSONB)  # Response summary (not full content)
    
    # Performance metrics
    response_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)
    cost_estimate = db.Column(db.Decimal(10, 4))
    
    # Status and error handling
    status_code = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text)
    
    # Client information
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    client_location = db.Column(JSONB)  # Country, region, city
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @classmethod
    def log_request(cls, user_id, endpoint, method, status_code, success, **kwargs):
        """Create a new usage log entry"""
        log_entry = cls(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            success=success,
            **kwargs
        )
        db.session.add(log_entry)
        return log_entry

class Invoice(db.Model):
    """Billing and invoice management"""
    
    __tablename__ = 'invoices'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Billing period
    billing_start = db.Column(db.DateTime, nullable=False)
    billing_end = db.Column(db.DateTime, nullable=False)
    
    # Financial details
    subtotal = db.Column(db.Decimal(12, 2), nullable=False)
    tax_amount = db.Column(db.Decimal(12, 2), default=0)
    discount_amount = db.Column(db.Decimal(12, 2), default=0)
    total_amount = db.Column(db.Decimal(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Payment information
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime)
    
    # Invoice details
    line_items = db.Column(JSONB)  # Detailed billing breakdown
    notes = db.Column(db.Text)
    
    # Due dates
    due_date = db.Column(db.DateTime, nullable=False)
    overdue_notice_sent = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number"""
        import time
        timestamp = int(time.time())
        return f"INV-{timestamp}"
    
    def to_dict(self):
        """Convert invoice to dictionary"""
        return {
            'id': str(self.id),
            'invoice_number': self.invoice_number,
            'billing_start': self.billing_start.isoformat(),
            'billing_end': self.billing_end.isoformat(),
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'payment_status': self.payment_status,
            'due_date': self.due_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class SystemSettings(db.Model):
    """Global system configuration and settings"""
    
    __tablename__ = 'system_settings'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(JSONB)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # api, billing, security, etc.
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    requires_admin = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a system setting value"""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set_setting(cls, key, value, description=None, category=None):
        """Set a system setting value"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(key=key, value=value, description=description, category=category)
            db.session.add(setting)
        return setting

class AuditLog(db.Model):
    """Security and compliance audit logging"""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, api_key_created, etc.
    event_category = db.Column(db.String(50))  # security, billing, project, system
    event_description = db.Column(db.Text)
    
    # Event data
    event_data = db.Column(JSONB)  # Additional event-specific data
    resource_type = db.Column(db.String(50))  # user, project, api_key, etc.
    resource_id = db.Column(db.String(100))
    
    # Request context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    
    # Security flags
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high, critical
    requires_attention = db.Column(db.Boolean, default=False)
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    @classmethod
    def log_event(cls, event_type, user_id=None, description=None, **kwargs):
        """Create a new audit log entry"""
        log_entry = cls(
            event_type=event_type,
            user_id=user_id,
            event_description=description,
            **kwargs
        )
        db.session.add(log_entry)
        return log_entry

# Database initialization and utility functions
def init_database(app):
    """Initialize database with application"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create default system settings
        default_settings = [
            ('api_rate_limit_default', 1000, 'Default API rate limit per hour'),
            ('subscription_trial_days', 30, 'Default trial period in days'),
            ('max_file_size_mb', 100, 'Maximum file upload size in MB'),
            ('supported_file_types', ['pdf', 'docx', 'txt', 'png', 'jpg'], 'Supported file types'),
            ('default_currency', 'USD', 'Default currency for billing'),
            ('tax_rate_default', 0.08, 'Default tax rate'),
            ('invoice_due_days', 30, 'Invoice due date in days'),
            ('password_min_length', 8, 'Minimum password length'),
            ('session_timeout_minutes', 60, 'Session timeout in minutes'),
            ('audit_log_retention_days', 365, 'Audit log retention period')
        ]
        
        for key, value, description in default_settings:
            if not SystemSettings.query.filter_by(key=key).first():
                setting = SystemSettings(key=key, value=value, description=description)
                db.session.add(setting)
        
        db.session.commit()

def create_sample_data():
    """Create sample data for development and testing"""
    # This would be used in development environment only
    if SystemSettings.get_setting('environment') == 'development':
        # Create sample users, projects, etc.
        pass