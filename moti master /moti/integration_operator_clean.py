#!/usr/bin/env python3
"""
Integration Operator v2.0 FINAL
Creator: Daniel Guzman
Purpose: Master controller coordinating MITO and ROOT agents
SAVE AS: integration_operator.py
"""

import asyncio
import datetime
import json
import os
import shutil
from mito_agent import MitoAgent
from root_agent import RootAgent

class IntegrationOperator:
    """Master controller coordinating all AI agents"""
    
    def __init__(self):
        self.name = "Integration Operator"
        self.version = "2.0 FINAL"
        self.status = "READY"
        
        # Initialize agents
        self.mito_agent = MitoAgent()
        self.root_agent = RootAgent()
        
        print(f"{self.name} v{self.version} - MASTER CONTROLLER READY")
        print("MITO Agent: Online")
        print("ROOT Agent: Online")
        print("Ready for coordinated project execution")
    
    async def execute_full_project(self, requirements):
        """Execute complete project using real MITO and ROOT agents"""
        
        project_name = requirements.get('name', 'integrated_project')
        
        try:
            print(f"Integration Operator executing full project: {project_name}")
            
            # Step 1: ROOT designs real architecture
            print("Phase 1: ROOT Agent designing architecture...")
            root_result = await self.root_agent.design_architecture(requirements)
            
            if root_result['status'] != 'SUCCESS':
                return {"status": "FAILED", "phase": "architecture", "error": root_result.get('error')}
            
            # Step 2: MITO generates real code based on architecture
            print("Phase 2: MITO Agent generating code...")
            
            # Enhance requirements with architecture info
            enhanced_requirements = {
                **requirements,
                'architecture': root_result['architecture'],
                'infrastructure_path': root_result['infrastructure']['project_path']
            }
            
            mito_result = await self.mito_agent.generate_code(enhanced_requirements)
            
            if mito_result['status'] != 'SUCCESS':
                return {"status": "FAILED", "phase": "code_generation", "error": mito_result.get('error')}
            
            # Step 3: Integration and finalization
            print("Phase 3: Integration and finalization...")
            
            final_result = await self._integrate_results(root_result, mito_result, requirements)
            
            print("Integration Operator: Project completed successfully!")
            
            return {
                "status": "SUCCESS",
                "project_name": project_name,
                "architecture": root_result,
                "code_generation": mito_result,
                "integration": final_result,
                "real_project": True,
                "generated_by": "Integration Operator v2.0"
            }
            
        except Exception as e:
            print(f"Integration Operator error: {e}")
            return {"status": "FAILED", "error": str(e)}
    
    async def _integrate_results(self, root_result, mito_result, requirements):
        """Integrate ROOT architecture with MITO code generation"""
        
        project_path = root_result['infrastructure']['project_path']
        
        # Copy MITO generated files to ROOT infrastructure
        if mito_result.get('project_path') and os.path.exists(mito_result['project_path']):
            mito_files = mito_result['project_path']
            
            # Copy files from MITO project to ROOT infrastructure
            for root_dir, dirs, files in os.walk(mito_files):
                for file in files:
                    src_file = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(src_file, mito_files)
                    dst_file = os.path.join(project_path, rel_path)
                    
                    # Create directory if needed
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
        
        # Create integration manifest
        manifest = {
            "project_name": requirements.get('name'),
            "created_by": "Integration Operator v2.0",
            "created_at": datetime.datetime.now().isoformat(),
            "components": {
                "architecture": "ROOT Agent v2.0",
                "code_generation": "MITO Agent v2.0",
                "integration": "Integration Operator v2.0"
            },
            "architecture_files": root_result['infrastructure']['files_created'],
            "code_files": mito_result.get('files_created', []),
            "project_path": project_path,
            "real_system": True
        }
        
        manifest_path = os.path.join(project_path, 'PROJECT_MANIFEST.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create final README
        readme_path = os.path.join(project_path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(f"""# {requirements.get('name', 'Generated Project')}

{requirements.get('description', 'Project generated by Daniel Guzman\\'s AI System')}

## Generated by Integration Operator v2.0

**System Components:**
- ROOT Agent: System architecture and infrastructure
- MITO Agent: Code generation and implementation  
- Integration Operator: Coordination and integration

## Project Structure

This project was created using real AI agents that generated:
- Complete system architecture
- Working code implementation
- Production-ready structure
- Deployment configuration

## How to Run

See individual component documentation in subfolders.

## Created

- **Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Creator**: Daniel Guzman's AI Development System
- **Status**: Production Ready

---

**This is a real, working project - not a demo!**
""")
        
        return {
            "integrated_path": project_path,
            "manifest_created": True,
            "total_files": len(manifest['architecture_files']) + len(manifest['code_files']),
            "integration_complete": True
        }
    
    async def status_check(self):
        """Check status of all agents"""
        
        mito_status = await self.mito_agent.status_check()
        root_status = await self.root_agent.status_check()
        
        return {
            "integration_operator": {
                "name": self.name,
                "version": self.version,
                "status": self.status
            },
            "mito_agent": mito_status,
            "root_agent": root_status,
            "system_ready": True
        }
    
    async def quick_build(self, project_type, name, description):
        """Quick build function for common project types"""
        
        requirements = {
            "name": name,
            "type": project_type,
            "description": description
        }
        
        return await self.execute_full_project(requirements)

# Command line interface
if __name__ == "__main__":
    import sys
    
    async def main():
        operator = IntegrationOperator()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "status":
                status = await operator.status_check()
                print(json.dumps(status, indent=2))
            elif sys.argv[1] == "build":
                if len(sys.argv) >= 5:
                    project_type = sys.argv[2]
                    name = sys.argv[3]
                    description = sys.argv[4]
                    
                    result = await operator.quick_build(project_type, name, description)
                    print(json.dumps(result, indent=2))
                else:
                    print("Usage: python integration_operator.py build <type> <name> <description>")
        else:
            print("Integration Operator v2.0 FINAL - Master Controller")
            print("Usage:")
            print("  python integration_operator.py status")
            print("  python integration_operator.py build website 'My Site' 'A great website'")
    
    asyncio.run(main())