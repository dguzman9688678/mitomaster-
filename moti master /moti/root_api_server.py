#!/usr/bin/env python3
"""
ROOT Agent API Server v2.0 FINAL
Creator: Daniel Guzman
Purpose: REST API server for ROOT Agent
SAVE AS: root_api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
import logging
from root_agent import RootAgent

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ROOT Agent
root_agent = RootAgent()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "agent": "ROOT",
            "version": root_agent.version,
            "timestamp": datetime.now().isoformat(),
            "capabilities": root_agent.capabilities
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Get ROOT agent status"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "agent": root_agent.name,
                "version": root_agent.version,
                "status": root_agent.status.value,
                "capabilities": root_agent.capabilities,
                "enterprise_tools_available": True
            },
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/architecture/design', methods=['POST'])
async def design_architecture():
    """Design system architecture"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Design architecture
        result = await root_agent.design_architecture(data)
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Architecture design failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/kubernetes/deploy', methods=['POST'])
async def create_kubernetes_deployment():
    """Create Kubernetes deployment manifests"""
    try:
        data = request.get_json()
        
        project_name = data.get('project_name')
        architecture = data.get('architecture', {})
        
        if not project_name:
            return jsonify({
                "success": False,
                "error": "project_name is required"
            }), 400
        
        result = await root_agent.create_kubernetes_deployment(project_name, architecture)
        
        return jsonify({
            "success": True,
            "data": {"k8s_manifests_path": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Kubernetes deployment creation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/terraform/create', methods=['POST'])
async def create_terraform_infrastructure():
    """Create Terraform infrastructure as code"""
    try:
        data = request.get_json()
        
        project_name = data.get('project_name')
        cloud_provider = data.get('cloud_provider', 'aws')
        
        if not project_name:
            return jsonify({
                "success": False,
                "error": "project_name is required"
            }), 400
        
        result = await root_agent.create_terraform_infrastructure(project_name, cloud_provider)
        
        return jsonify({
            "success": True,
            "data": {"terraform_path": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Terraform infrastructure creation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/security/scan', methods=['POST'])
async def create_security_scanning():
    """Setup security scanning and compliance"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await root_agent.create_security_scanning(project_path)
        
        return jsonify({
            "success": True,
            "data": {"security_setup": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Security scanning setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/disaster-recovery/setup', methods=['POST'])
async def setup_disaster_recovery():
    """Setup disaster recovery and backup systems"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        project_name = data.get('project_name')
        
        if not project_path or not project_name:
            return jsonify({
                "success": False,
                "error": "project_path and project_name are required"
            }), 400
        
        result = await root_agent.create_disaster_recovery(project_path, project_name)
        
        return jsonify({
            "success": True,
            "data": {"disaster_recovery_setup": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Disaster recovery setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/performance/setup', methods=['POST'])
async def setup_performance_monitoring():
    """Setup performance monitoring and optimization"""
    try:
        data = request.get_json()
        
        project_path = data.get('project_path')
        
        if not project_path:
            return jsonify({
                "success": False,
                "error": "project_path is required"
            }), 400
        
        result = await root_agent.create_performance_optimization(project_path)
        
        return jsonify({
            "success": True,
            "data": {"performance_setup": result},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Performance monitoring setup failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/infrastructure/check', methods=['GET'])
def check_infrastructure_tools():
    """Check availability of infrastructure tools"""
    try:
        tools_status = {
            "kubernetes": root_agent._check_kubernetes(),
            "docker": root_agent._check_docker(),
            "terraform": root_agent._check_terraform(),
            "ansible": root_agent._check_ansible(),
            "aws_cli": root_agent._check_aws_cli(),
            "azure_cli": root_agent._check_azure_cli(),
            "gcp_cli": root_agent._check_gcp_cli()
        }
        
        return jsonify({
            "success": True,
            "data": {
                "infrastructure_tools": tools_status,
                "total_available": sum(tools_status.values()),
                "total_tools": len(tools_status)
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Infrastructure check failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/architectures', methods=['GET'])
def list_architectures():
    """List all created architectures"""
    try:
        projects_dir = "./projects"
        architectures = []
        
        if os.path.exists(projects_dir):
            for item in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, item)
                if os.path.isdir(project_path):
                    # Check for architecture files
                    arch_file = os.path.join(project_path, "ARCHITECTURE.md")
                    if os.path.exists(arch_file):
                        arch_info = {
                            "name": item,
                            "path": project_path,
                            "has_kubernetes": os.path.exists(os.path.join(project_path, "k8s")),
                            "has_terraform": os.path.exists(os.path.join(project_path, "terraform")),
                            "has_security": os.path.exists(os.path.join(project_path, "security")),
                            "has_disaster_recovery": os.path.exists(os.path.join(project_path, "disaster-recovery")),
                            "has_performance": os.path.exists(os.path.join(project_path, "performance"))
                        }
                        architectures.append(arch_info)
        
        return jsonify({
            "success": True,
            "data": {
                "architectures": architectures,
                "total": len(architectures)
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Architecture listing failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/capabilities', methods=['GET'])
def get_capabilities():
    """Get ROOT agent capabilities"""
    return jsonify({
        "success": True,
        "data": {
            "agent": "ROOT",
            "version": root_agent.version,
            "capabilities": root_agent.capabilities,
            "endpoints": [
                "POST /api/v1/architecture/design - Design system architecture",
                "POST /api/v1/kubernetes/deploy - Create Kubernetes manifests",
                "POST /api/v1/terraform/create - Create Terraform infrastructure",
                "POST /api/v1/security/scan - Setup security scanning",
                "POST /api/v1/disaster-recovery/setup - Setup disaster recovery",
                "POST /api/v1/performance/setup - Setup performance monitoring",
                "GET /api/v1/infrastructure/check - Check infrastructure tools",
                "GET /api/v1/architectures - List architectures",
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
            "POST /api/v1/architecture/design",
            "POST /api/v1/kubernetes/deploy",
            "POST /api/v1/terraform/create",
            "POST /api/v1/security/scan",
            "POST /api/v1/disaster-recovery/setup",
            "POST /api/v1/performance/setup",
            "GET /api/v1/infrastructure/check",
            "GET /api/v1/architectures",
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
    print("Starting ROOT Agent API Server...")
    print("Available endpoints:")
    print("  GET  /health")
    print("  GET  /api/v1/status")
    print("  POST /api/v1/architecture/design")
    print("  POST /api/v1/kubernetes/deploy")
    print("  POST /api/v1/terraform/create")
    print("  POST /api/v1/security/scan")
    print("  POST /api/v1/disaster-recovery/setup")
    print("  POST /api/v1/performance/setup")
    print("  GET  /api/v1/infrastructure/check")
    print("  GET  /api/v1/architectures")
    print("  GET  /api/v1/capabilities")
    print("")
    print("ROOT Agent API Server ready on http://localhost:5002")
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
        threaded=True
    )