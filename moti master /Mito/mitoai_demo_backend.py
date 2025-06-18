# app.py - MitoAI Demo Backend
# © 2025 Daniel Guzman - All Rights Reserved
# Contact: guzman.daniel@outlook.com

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
import json
import requests
from datetime import datetime
import base64

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-key-here')

# AI Operator - The Brain of MitoAI
class AIOperator:
    def __init__(self):
        self.tools = {
            'content_tool': self.generate_content,
            'image_tool': self.generate_image,
            'weather_tool': self.get_weather_context,
            'voice_tool': self.process_voice,
            'book_tool': self.format_book
        }
    
    def process_request(self, user_intent, location=None):
        """AI decides which tools to use based on user intent"""
        try:
            # AI analyzes intent and selects tools
            analysis_prompt = f"""
            User Request: "{user_intent}"
            
            Available Tools:
            - content: Create stories, articles, written content
            - image: Generate illustrations, pictures, visuals
            - weather: Include weather data (if location provided)
            - voice: Process audio input/output
            - book: Format content into publication
            
            Determine what the user wants. Respond with JSON only:
            {{"action": "content|image|both", "needs_weather": true/false, "content_type": "story|article|business|educational"}}
            """
            
            decision = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            try:
                ai_decision = json.loads(decision.choices[0].message.content)
            except:
                # Fallback if JSON parsing fails
                ai_decision = {"action": "content", "needs_weather": False, "content_type": "story"}
            
            # Execute based on AI decision
            result = {}
            
            # Get weather context if needed
            weather_context = ""
            if ai_decision.get('needs_weather') and location:
                weather_context = self.get_weather_context(location)
            
            # Generate content
            if ai_decision['action'] in ['content', 'both']:
                enhanced_prompt = f"{weather_context}\n\nUser request: {user_intent}"
                result['content'] = self.generate_content(enhanced_prompt, ai_decision.get('content_type', 'story'))
            
            # Generate image
            if ai_decision['action'] in ['image', 'both']:
                result['image'] = self.generate_image(user_intent)
            
            return {
                'success': True,
                'ai_decision': ai_decision,
                'result': result,
                'weather_used': bool(weather_context)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_content(self, prompt, content_type='story'):
        """Generate content using OpenAI"""
        try:
            system_prompts = {
                'story': 'You are a professional storyteller. Create engaging, well-structured stories.',
                'article': 'You are a professional writer. Create informative, well-researched articles.',
                'business': 'You are a business consultant. Create professional, actionable business content.',
                'educational': 'You are an educator. Create clear, informative educational content.'
            }
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompts.get(content_type, system_prompts['story'])},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Content generation error: {str(e)}"
    
    def generate_image(self, prompt):
        """Generate image using DALL-E"""
        try:
            # Enhance prompt for better results
            enhanced_prompt = f"Professional, high-quality illustration: {prompt}. Digital art style, detailed, vibrant colors."
            
            response = openai.Image.create(
                prompt=enhanced_prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3"
            )
            
            return response.data[0].url
            
        except Exception as e:
            return f"Image generation error: {str(e)}"
    
    def get_weather_context(self, location):
        """Get weather data from NOAA (free API)"""
        try:
            # Simple weather context - you can enhance this
            lat, lon = location.get('lat', 40.7128), location.get('lon', -74.0060)  # Default to NYC
            
            # NOAA API call
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            points_response = requests.get(points_url)
            
            if points_response.status_code == 200:
                forecast_url = points_response.json()['properties']['forecast']
                weather_response = requests.get(forecast_url)
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    current_weather = weather_data['properties']['periods'][0]
                    
                    return f"Current weather: {current_weather['shortForecast']}, {current_weather['temperature']}°F. "
            
            return ""
            
        except:
            return ""
    
    def process_voice(self, audio_data):
        """Process voice input using Whisper"""
        # Placeholder for voice processing
        return "Voice processing not implemented in demo"
    
    def format_book(self, content, images=None):
        """Format content into book layout"""
        # Simple book formatting
        formatted = f"""
        <div class="book-preview">
            <h1>Generated Book</h1>
            <div class="book-content">
                {content}
            </div>
            {f'<div class="book-images"><img src="{images}" alt="Book illustration"></div>' if images else ''}
        </div>
        """
        return formatted

# Initialize AI Operator
ai_operator = AIOperator()

# Routes
@app.route('/')
def home():
    """Serve the main platform interface"""
    return send_from_directory('static', 'index.html')

@app.route('/api/ai-operator', methods=['POST'])
def ai_operator_endpoint():
    """Main AI Operator endpoint"""
    data = request.json
    user_intent = data.get('intent', '')
    location = data.get('location')
    
    if not user_intent:
        return jsonify({'success': False, 'error': 'No intent provided'})
    
    result = ai_operator.process_request(user_intent, location)
    return jsonify(result)

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """Direct content generation endpoint"""
    data = request.json
    prompt = data.get('prompt', '')
    content_type = data.get('type', 'story')
    
    try:
        content = ai_operator.generate_content(prompt, content_type)
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Direct image generation endpoint"""
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        image_url = ai_operator.generate_image(prompt)
        return jsonify({'success': True, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/weather-story', methods=['POST'])
def weather_story():
    """Weather-enhanced content generation"""
    data = request.json
    prompt = data.get('prompt', '')
    location = data.get('location')
    
    try:
        weather_context = ai_operator.get_weather_context(location) if location else ""
        enhanced_prompt = f"{weather_context}\n\n{prompt}"
        content = ai_operator.generate_content(enhanced_prompt)
        
        return jsonify({
            'success': True,
            'content': content,
            'weather_used': bool(weather_context)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'platform': 'MitoAI by Daniel Guzman',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting MitoAI Platform by Daniel Guzman")
    print("📧 Contact: guzman.daniel@outlook.com")
    print("🌐 Platform starting on http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )