#!/usr/bin/env python3
"""
MITO Agent API Server v2.0 FINAL
Creator: Daniel Guzman
Purpose: REST API server for MITO Agent
SAVE AS: mito_api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
import logging
from mito_agent import MitoAgent

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MITO Agent
mito_agent = MitoAgent()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "agent": "MITO",
            "version": mito_agent.version,
            "timestamp": datetime.now().isoformat(),
            "capabilities": mito_agent.capabilities
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/status', methods=['GET'])
async def get_status():
    """Get MITO agent status"""
    try:
        status = await mito_agent.status_check()
        return jsonify({
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/generate', methods=['POST'])
async def generate_code():
    """Generate code using MITO agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Generate code
        result = await mito_agent.generate_code(data)
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/database/setup', methods=['POST'])
async def setup_database():
    """Setup database for project"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        db_type = data.get('db_type', 'sqlite')
        connection_params = data.get('connection_params')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.setup_database(project_path, db_type, connection_params)
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/git/setup', methods=['POST'])
async def setup_git():
    """Setup Git repository for project"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        repo_url = data.get('repo_url')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.setup_git_repository(project_path, repo_url)
        
        return jsonify({
            "success": True,
            "data": {"git_setup": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Git setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/cicd/create', methods=['POST'])
async def create_cicd():
    """Create CI/CD pipeline"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        platform = data.get('platform', 'github')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.create_cicd_pipeline(project_path, platform)
        
        return jsonify({
            "success": True,
            "data": {"cicd_created": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"CI/CD creation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/deploy', methods=['POST'])
async def deploy_to_cloud():
    """Deploy project to cloud platform"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        platform = data.get('platform', 'aws')
        deployment_config = data.get('deployment_config', {})
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.deploy_to_cloud(project_path, platform, deployment_config)
        
        return jsonify({
            "success": True,
            "data": {"deployment": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Cloud deployment failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/monitoring/setup', methods=['POST'])
async def setup_monitoring():
    """Setup monitoring for project"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.create_monitoring_setup(project_path)
        
        return jsonify({
            "success": True,
            "data": {"monitoring_setup": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Monitoring setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/testing/create', methods=['POST'])
async def create_testing():
    """Create testing suite for project"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await mito_agent.create_testing_suite(project_path)
        
        return jsonify({
            "success": True,
            "data": {"testing_suite": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Testing suite creation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/projects', methods=['GET'])
def list_projects():
    """List all generated projects"""
    try:
        projects_dir = "./projects"
        projects = []
        
        if os.path.exists(projects_dir):
            for item in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, item)
                if os.path.isdir(project_path):
                    # Get project manifest if exists
                    manifest_path = os.path.join(project_path, "PROJECT_MANIFEST.json")
                    project_info = {"name": item, "path": project_path}
                    
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r') as f:
                                manifest = json.load(f)
                            project_info.update(manifest)
                        except:
                            pass
                    
                    projects.append(project_info)
        
        return jsonify({
            "success": True,
            "data": {
                "projects": projects,
                "total": len(projects)
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Project listing failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/capabilities', methods=['GET'])
def get_capabilities():
    """Get MITO agent capabilities"""
    return jsonify({
        "success": True,
        "data": {
            "agent": "MITO",
            "version": mito_agent.version,
            "capabilities": mito_agent.capabilities,
            "endpoints": [
                "POST /api/v1/generate - Generate code",
                "POST /api/v1/database/setup - Setup database",
                "POST /api/v1/git/setup - Setup Git repository",
                "POST /api/v1/cicd/create - Create CI/CD pipeline",
                "POST /api/v1/deploy - Deploy to cloud",
                "POST /api/v1/monitoring/setup - Setup monitoring",
                "POST /api/v1/testing/create - Create testing suite",
                "GET /api/v1/projects - List projects",
                "GET /api/v1/status - Get agent status"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "GET /api/v1/status",
            "POST /api/v1/generate",
            "POST /api/v1/database/setup",
            "POST /api/v1/git/setup",
            "POST /api/v1/cicd/create",
            "POST /api/v1/deploy",
            "POST /api/v1/monitoring/setup",
            "POST /api/v1/testing/create",
            "GET /api/v1/projects",
            "GET /api/v1/capabilities"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("Starting MITO Agent API Server...")
    print("Available endpoints:")
    print("  GET  /health")
    print("  GET  /api/v1/status")
    print("  POST /api/v1/generate")
    print("  POST /api/v1/database/setup")
    print("  POST /api/v1/git/setup")
    print("  POST /api/v1/cicd/create")
    print("  POST /api/v1/deploy")
    print("  POST /api/v1/monitoring/setup")
    print("  POST /api/v1/testing/create")
    print("  GET  /api/v1/projects")
    print("  GET  /api/v1/capabilities")
    print("")
    print("MITO Agent API Server ready on http://localhost:5001")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )