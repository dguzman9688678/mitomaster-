"""
MitoAI Platform - Professional Backend Implementation
Creator: Daniel Guzman
Contact: guzman.daniel@outlook.com
Copyright: 2025 Daniel Guzman - All Rights Reserved

NO ONE IS AUTHORIZED TO ALTER THIS SOFTWARE UNLESS AUTHORIZED BY DANIEL GUZMAN
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
import json
import requests
from datetime import datetime
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
app.wsgi_app = ProxyFix(app.wsgi_app)
CORS(app)

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mitoai-daniel-guzman-2025')
    
    @staticmethod
    def init_app(app):
        pass

app.config.from_object(Config)

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY

class AIOperatorEngine:
    """
    AI Operator Engine - Core Intelligence System
    Processes user requests and orchestrates appropriate AI tools
    """
    
    def __init__(self):
        self.available_tools = {
            'content_generation': self.generate_content,
            'image_generation': self.generate_image,
            'weather_integration': self.integrate_weather_data,
            'voice_processing': self.process_voice_input,
            'document_formatting': self.format_document
        }
        
    def process_user_request(self, user_intent, location=None, preferences=None):
        """
        Analyze user intent and execute appropriate AI tools
        
        Args:
            user_intent (str): User's natural language request
            location (dict): Optional location data for weather integration
            preferences (dict): Optional user preferences
            
        Returns:
            dict: Processing results with AI decisions and outputs
        """
        try:
            # AI intent analysis
            intent_analysis = self._analyze_user_intent(user_intent)
            
            # Weather context if location provided
            weather_context = ""
            if location and intent_analysis.get('requires_weather', False):
                weather_context = self.integrate_weather_data(location)
            
            # Execute selected tools
            execution_results = self._execute_tool_sequence(
                intent_analysis, user_intent, weather_context, preferences
            )
            
            return {
                'success': True,
                'intent_analysis': intent_analysis,
                'weather_context': weather_context,
                'results': execution_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI Operator processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_user_intent(self, user_intent):
        """Analyze user intent using OpenAI"""
        analysis_prompt = f"""
        Analyze this user request and determine the appropriate response strategy:
        
        Request: "{user_intent}"
        
        Determine:
        1. Primary action needed (content, image, both, analysis)
        2. Content type if applicable (story, article, business, educational, creative)
        3. Whether weather context would enhance the response
        4. Complexity level (simple, moderate, complex)
        
        Respond with valid JSON only:
        {{
            "primary_action": "content|image|both|analysis",
            "content_type": "story|article|business|educational|creative",
            "requires_weather": true/false,
            "complexity": "simple|moderate|complex",
            "estimated_tokens": 500
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except json.JSONDecodeError:
            # Fallback analysis
            return {
                "primary_action": "content",
                "content_type": "story",
                "requires_weather": False,
                "complexity": "moderate",
                "estimated_tokens": 500
            }
    
    def _execute_tool_sequence(self, analysis, user_intent, weather_context, preferences):
        """Execute the determined sequence of AI tools"""
        results = {}
        
        # Content generation
        if analysis['primary_action'] in ['content', 'both']:
            enhanced_prompt = self._enhance_prompt(user_intent, weather_context, preferences)
            results['content'] = self.generate_content(enhanced_prompt, analysis['content_type'])
        
        # Image generation
        if analysis['primary_action'] in ['image', 'both']:
            image_prompt = self._create_image_prompt(user_intent, results.get('content'))
            results['image'] = self.generate_image(image_prompt)
        
        return results
    
    def _enhance_prompt(self, base_prompt, weather_context, preferences):
        """Enhance user prompt with context and preferences"""
        enhanced = base_prompt
        
        if weather_context:
            enhanced = f"Weather context: {weather_context}\n\nRequest: {enhanced}"
        
        if preferences:
            style_note = f"User preferences: {preferences.get('style', 'professional')}"
            enhanced = f"{style_note}\n\n{enhanced}"
        
        return enhanced
    
    def _create_image_prompt(self, user_intent, generated_content=None):
        """Create optimized prompt for image generation"""
        if generated_content:
            # Extract key visual elements from generated content
            visual_prompt = f"Create professional illustration based on: {user_intent}. Style: high-quality digital art, detailed, professional composition."
        else:
            visual_prompt = f"Professional illustration: {user_intent}. High-quality digital art style, detailed composition, vibrant colors."
        
        return visual_prompt
    
    def generate_content(self, prompt, content_type='story'):
        """Generate text content using OpenAI GPT models"""
        try:
            system_prompts = {
                'story': 'You are a professional storyteller specializing in engaging, well-structured narratives.',
                'article': 'You are a professional content writer creating informative, well-researched articles.',
                'business': 'You are a business consultant creating professional, actionable business content.',
                'educational': 'You are an expert educator creating clear, informative educational materials.',
                'creative': 'You are a creative writer producing original, imaginative content.'
            }
            
            system_message = system_prompts.get(content_type, system_prompts['story'])
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            return f"Content generation temporarily unavailable. Error: {str(e)}"
    
    def generate_image(self, prompt):
        """Generate images using OpenAI DALL-E"""
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3"
            )
            
            return response.data[0].url
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            return None
    
    def integrate_weather_data(self, location):
        """Integrate weather data from NOAA API"""
        try:
            lat = location.get('lat', 40.7128)
            lon = location.get('lon', -74.0060)
            
            # NOAA Weather API integration
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            points_response = requests.get(points_url, timeout=10)
            
            if points_response.status_code == 200:
                forecast_url = points_response.json()['properties']['forecast']
                weather_response = requests.get(forecast_url, timeout=10)
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    current_period = weather_data['properties']['periods'][0]
                    
                    return f"Current weather: {current_period['shortForecast']}, {current_period['temperature']}°F. "
            
            return ""
            
        except Exception as e:
            logger.error(f"Weather integration error: {str(e)}")
            return ""
    
    def process_voice_input(self, audio_data):
        """Process voice input using OpenAI Whisper"""
        # Placeholder for voice processing implementation
        return "Voice processing functionality ready for implementation"
    
    def format_document(self, content, format_type='html'):
        """Format content into various document types"""
        if format_type == 'html':
            return f"""
            <div class="generated-document">
                <div class="document-header">
                    <h2>Generated Content</h2>
                    <p class="timestamp">Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                <div class="document-content">
                    {content.replace('\n', '<br>')}
                </div>
                <div class="document-footer">
                    <p>Generated by MitoAI Platform - Daniel Guzman</p>
                </div>
            </div>
            """
        return content

# Initialize AI Operator
ai_operator = AIOperatorEngine()

# API Routes
@app.route('/')
def index():
    """Serve main application interface"""
    return send_from_directory('static', 'index.html')

@app.route('/api/ai-operator', methods=['POST'])
def ai_operator_endpoint():
    """Main AI Operator processing endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'intent' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request format. Intent required.'
            }), 400
        
        user_intent = data['intent']
        location = data.get('location')
        preferences = data.get('preferences', {})
        
        # Process through AI Operator
        result = ai_operator.process_user_request(user_intent, location, preferences)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI Operator endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal processing error'
        }), 500

@app.route('/api/generate-content', methods=['POST'])
def generate_content_endpoint():
    """Direct content generation endpoint"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        content_type = data.get('type', 'story')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt required'
            }), 400
        
        content = ai_operator.generate_content(prompt, content_type)
        
        return jsonify({
            'success': True,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Content generation endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Content generation failed'
        }), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image_endpoint():
    """Direct image generation endpoint"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Image prompt required'
            }), 400
        
        image_url = ai_operator.generate_image(prompt)
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Image generation endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Image generation failed'
        }), 500

@app.route('/api/weather-enhanced-content', methods=['POST'])
def weather_enhanced_content():
    """Weather-enhanced content generation"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        location = data.get('location')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Content prompt required'
            }), 400
        
        # Get weather context
        weather_context = ai_operator.integrate_weather_data(location) if location else ""
        
        # Generate enhanced content
        enhanced_prompt = f"{weather_context}\n\n{prompt}" if weather_context else prompt
        content = ai_operator.generate_content(enhanced_prompt)
        
        return jsonify({
            'success': True,
            'content': content,
            'weather_context': weather_context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Weather-enhanced content error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Weather-enhanced content generation failed'
        }), 500

@app.route('/api/platform-status', methods=['GET'])
def platform_status():
    """Platform health and status endpoint"""
    return jsonify({
        'status': 'operational',
        'platform': 'MitoAI Professional Platform',
        'creator': 'Daniel Guzman',
        'contact': 'guzman.daniel@outlook.com',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ai_operator': 'active',
            'content_generation': 'active',
            'image_generation': 'active',
            'weather_integration': 'active'
        }
    })

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Resource not found',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status_code': 500
    }), 500

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        'error': 'Invalid request format',
        'status_code': 400
    }), 400

# Application initialization
def create_app():
    """Application factory pattern"""
    Config.init_app(app)
    return app

if __name__ == '__main__':
    print("MitoAI Platform - Professional Edition")
    print("Creator: Daniel Guzman")
    print("Contact: guzman.daniel@outlook.com")
    print("Copyright: 2025 Daniel Guzman - All Rights Reserved")
    print("Server starting on port 5000")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(Config.FLASK_ENV == 'development')
    )