"""
MitoAI Platform - Simple Backend for Beginners
Creator: Daniel Guzman
Contact: guzman.daniel@outlook.com
Copyright: 2025 Daniel Guzman - All Rights Reserved

SIMPLIFIED VERSION FOR 5 WEEKS CODING EXPERIENCE
This is much easier to understand and implement
"""

from flask import Flask, request, jsonify, render_template
import openai
import os
from datetime import datetime
import json

# Simple Flask app setup
app = Flask(__name__)

# Configuration - Just add your OpenAI key here
openai.api_key = "your-openai-key-here"  # Replace with your actual key

# Simple in-memory storage (no database needed for now)
users = {}
projects = {}
usage_stats = {}

# Simple AI Helper Class
class SimpleAI:
    """Simple AI helper that anyone can understand"""
    
    def generate_content(self, prompt, content_type="story"):
        """Generate content using OpenAI"""
        try:
            if content_type == "business_plan":
                system_message = "You are a professional business consultant. Create detailed business plans."
            elif content_type == "story":
                system_message = "You are a professional storyteller. Create engaging stories."
            else:
                system_message = "You are a professional writer. Create high-quality content."
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_image(self, prompt):
        """Generate image using DALL-E"""
        try:
            response = openai.Image.create(
                prompt=f"Professional, high-quality: {prompt}",
                n=1,
                size="1024x1024"
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create AI helper
ai_helper = SimpleAI()

# SIMPLE ROUTES - Easy to understand

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """Generate content - SIMPLE VERSION"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        content_type = data.get('type', 'story')
        
        if not prompt:
            return jsonify({"error": "Please provide a prompt"}), 400
        
        # Use AI helper to generate content
        result = ai_helper.generate_content(prompt, content_type)
        
        # Track usage (simple counter)
        if 'total_requests' not in usage_stats:
            usage_stats['total_requests'] = 0
        usage_stats['total_requests'] += 1
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate image - SIMPLE VERSION"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Please provide an image description"}), 400
        
        # Use AI helper to generate image
        result = ai_helper.generate_image(prompt)
        
        # Track usage
        if 'total_images' not in usage_stats:
            usage_stats['total_images'] = 0
        usage_stats['total_images'] += 1
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-business-plan', methods=['POST'])
def create_business_plan():
    """Create business plan - SIMPLE VERSION"""
    try:
        data = request.json
        business_idea = data.get('business_idea', '')
        industry = data.get('industry', '')
        
        if not business_idea:
            return jsonify({"error": "Please describe your business idea"}), 400
        
        # Create detailed prompt for business plan
        prompt = f"""
        Create a comprehensive business plan for this idea:
        Business Idea: {business_idea}
        Industry: {industry}
        
        Include:
        1. Executive Summary
        2. Market Analysis
        3. Business Model
        4. Financial Projections
        5. Marketing Strategy
        6. Risk Analysis
        7. Implementation Plan
        """
        
        # Generate business plan
        result = ai_helper.generate_content(prompt, "business_plan")
        
        # Track usage
        if 'business_plans' not in usage_stats:
            usage_stats['business_plans'] = 0
        usage_stats['business_plans'] += 1
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-consultant', methods=['POST'])
def ai_consultant():
    """AI Business Consultant - SIMPLE VERSION"""
    try:
        data = request.json
        question = data.get('question', '')
        industry = data.get('industry', 'general')
        
        if not question:
            return jsonify({"error": "Please ask a question"}), 400
        
        # Create consultant prompt
        prompt = f"""
        You are a senior business consultant with 20+ years of experience.
        Industry focus: {industry}
        
        Client question: {question}
        
        Provide professional, actionable advice with:
        1. Direct answer to the question
        2. Specific recommendations
        3. Implementation steps
        4. Potential risks and how to avoid them
        5. Expected outcomes
        """
        
        result = ai_helper.generate_content(prompt, "consultant")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics - SIMPLE VERSION"""
    return jsonify({
        "platform": "MitoAI by Daniel Guzman",
        "status": "operational",
        "usage_stats": usage_stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        "status": "healthy",
        "platform": "MitoAI",
        "creator": "Daniel Guzman",
        "contact": "guzman.daniel@outlook.com"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500

# SIMPLE STARTUP
if __name__ == '__main__':
    print("=" * 50)
    print("MitoAI Platform - Simple Version")
    print("Creator: Daniel Guzman")
    print("Contact: guzman.daniel@outlook.com")
    print("=" * 50)
    print("INSTRUCTIONS:")
    print("1. Add your OpenAI API key at the top of this file")
    print("2. Install requirements: pip install flask openai")
    print("3. Run this file: python app.py")
    print("4. Open browser to: http://localhost:5000")
    print("=" * 50)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)