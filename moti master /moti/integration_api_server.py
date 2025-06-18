#!/usr/bin/env python3
"""
Integration Operator API Server v2.0 FINAL
Creator: Daniel Guzman
Purpose: REST API server for Integration Operator (coordinates MITO and ROOT)
SAVE AS: integration_api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import os
import requests
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent endpoints
MITO_API_URL = "http://localhost:5001"
ROOT_API_URL = "http://localhost:5002"

class IntegrationOperatorAPI:
    """Integration Operator API - Coordinates MITO and ROOT agents via API calls"""
    
    def __init__(self):
        self.name = "Integration Operator"
        self.version = "2.0 FINAL API"
        self.mito_url = MITO_API_URL
        self.root_url = ROOT_API_URL
    
    async def check_agents_health(self):
        """Check if MITO and ROOT agents are healthy"""
        try:
            mito_health = requests.get(f"{self.mito_url}/health", timeout=5)
            root_health = requests.get(f"{self.root_url}/health", timeout=5)
            
            return {
                "mito_healthy": mito_health.status_code == 200,
                "root_healthy": root_health.status_code == 200,
                "mito_status": mito_health.json() if mito_health.status_code == 200 else None,
                "root_status": root_health.json() if root_health.status_code == 200 else None
            }
        except Exception as e:
            return {
                "mito_healthy": False,
                "root_healthy": False,
                "error": str(e)
            }
    
    async def execute_full_project(self, requirements):
        """Execute complete project using MITO and ROOT agents via API"""
        project_name = requirements.get('name', 'integrated_project')
        
        try:
            # Phase 1: ROOT designs architecture
            logger.info("Phase 1: ROOT Agent designing architecture...")
            
            root_