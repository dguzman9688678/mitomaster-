"""
MitoAI Platform - Enhanced API Routes
Creator: Daniel Guzman
Contact: guzman.daniel@outlook.com
Copyright: 2025 Daniel Guzman - All Rights Reserved

NO ONE IS AUTHORIZED TO ALTER THIS SOFTWARE UNLESS AUTHORIZED BY DANIEL GUZMAN

Complete API routes for enterprise web application
"""

from flask import Blueprint, request, jsonify, g, current_app
from flask_limiter import Limiter # type: ignore
from flask_limiter.util import get_remote_address
from functools import wraps
import jwt
from datetime import datetime, timedelta
import uuid
import hashlib
import hmac
from models import (
    db, User, APIKey, Project, ProjectTask, ProjectFile, 
    UsageLog, Invoice, SystemSettings, AuditLog,
    SubscriptionTier, ProjectStatus, APIKeyStatus
)
from ai_services import AIOperatorEngine, get_business_model_instance
import os
import logging

# Create blueprints for different API sections
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
users_bp = Blueprint('users', __name__, url_prefix='/api/users')
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')
billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Initialize AI engine
ai_engine = AIOperatorEngine()

# Logging setup
logger = logging.getLogger(__name__)

# Authentication decorators
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'Invalid token'}), 401
            
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def api_key_required(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-MitoAI-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        
        # Hash the provided key to compare with stored hash
        api_key_record = None
        for key_record in APIKey.query.filter_by(status=APIKeyStatus.ACTIVE).all():
            if key_record.check_key(api_key):
                api_key_record = key_record
                break
        
        if not api_key_record:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Check if key is expired
        if api_key_record.expires_at and datetime.utcnow() > api_key_record.expires_at:
            return jsonify({'error': 'API key has expired'}), 401
        
        # Update usage statistics
        api_key_record.last_used = datetime.utcnow()
        api_key_record.total_requests += 1
        
        g.current_user = api_key_record.user
        g.current_api_key = api_key_record
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.subscription_tier != SubscriptionTier.UNLIMITED:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    
    return decorated

# Authentication Routes
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""