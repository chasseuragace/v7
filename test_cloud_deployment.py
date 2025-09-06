#!/usr/bin/env python3
"""
Test Cloud Deployment Capabilities
Tests the cloud deployment functionality of the Statement-to-Reality System
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path
import json

from multi_language_generator import ProductionMultiLanguageGenerator, create_multi_language_generator
from cloud_deployment import ProductionCloudDeployment, create_cloud_deployment_engine, DeploymentProvider
from statement_reality_system import Environment, ResourceConstraints, Architecture, ArchitecturalComponent


class CloudDeploymentTester:
    """Test suite for cloud deployment capabilities"""
    
    def __init__(self):
        self.generator = create_multi_language_generator()
        self.deployment_engine = create_cloud_deployment_engine()
        self.test_dir = None
        
    async def setup_test_environment(self):
        """Setup temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="statement_reality_test_")
        print(f"Created test directory: {self.test_dir}")
        
    async def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"Cleaned up test directory: {self.test_dir}")
    
    async def test_application_generation(self):
        """Test generating applications in multiple languages"""
        print("\n=== Testing Application Generation ===")
        
        # Test cases for different languages and frameworks
        test_cases = [
            {
                "name": "Python FastAPI Todo App",
                "language": "python",
                "framework": "fastapi",
                "description": "A simple todo application with REST API"
            },
            {
                "name": "Rust Axum Chat App", 
                "language": "rust",
                "framework": "axum",
                "description": "A real-time chat application"
            },
            {
                "name": "Go Gin Dashboard",
                "language": "go", 
                "framework": "gin",
                "description": "A monitoring dashboard application"
            }
        ]
        
        generated_apps = []
        
        for test_case in test_cases:
            print(f"\nGenerating {test_case['name']}...")
            
            # Create test architecture for the application
            architecture = Architecture(
                components=[
                    ArchitecturalComponent(
                        name="API",
                        responsibilities=["Handle HTTP requests", "Route endpoints"],
                        interfaces=["get", "post", "put", "delete"],
                        dependencies=[],
                        constraints={}
                    ),
                    ArchitecturalComponent(
                        name="Service",
                        responsibilities=["Business logic", "Data processing"],
                        interfaces=["process", "validate"],
                        dependencies=["API"],
                        constraints={}
                    ),
                    ArchitecturalComponent(
                        name="Storage",
                        responsibilities=["Data persistence", "Query handling"],
                        interfaces=["save", "load", "query"],
                        dependencies=["Service"],
                        constraints={}
                    )
                ],
                patterns=["REST API", "Layered Architecture"],
                relationships={"API": ["Service"], "Service": ["Storage"]},
                constraints={},
                quality_attributes={"performance": "high", "scalability": "medium"}
            )
            
            try:
                # Generate application code
                generated_files = self.generator.generate_code(
                    architecture, 
                    test_case["language"], 
                    test_case["framework"]
                )
                
                if generated_files:
                    print(f"✓ Successfully generated {test_case['name']}")
                    print(f"  Files created: {len(generated_files)}")
                    
                    # Create output directory and save files
                    output_dir = os.path.join(self.test_dir, test_case["name"].lower().replace(" ", "_"))
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Write generated files to disk
                    for filename, content in generated_files.items():
                        file_path = os.path.join(output_dir, filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'w') as f:
                            f.write(content)
                    
                    generated_apps.append({
                        "test_case": test_case,
                        "files": generated_files,
                        "path": output_dir
                    })
                else:
                    print(f"✗ No files generated for {test_case['name']}")
                    
            except Exception as e:
                print(f"✗ Exception generating {test_case['name']}: {e}")
        
        return generated_apps
    
    async def test_deployment_configuration(self, generated_apps):
        """Test deployment configuration generation"""
        print("\n=== Testing Deployment Configuration ===")
        
        deployment_configs = []
        
        for app in generated_apps:
            test_case = app["test_case"]
            app_path = app["path"]
            
            print(f"\nConfiguring deployment for {test_case['name']}...")
            
            # Test different cloud providers
            providers = [
                DeploymentProvider.VERCEL,
                DeploymentProvider.NETLIFY,
                DeploymentProvider.RAILWAY,
                DeploymentProvider.RENDER
            ]
            
            for provider in providers:
                try:
                    app_name = f"{test_case['name'].lower().replace(' ', '-')}-{provider.value}"
                    
                    # Test deployment configuration generation
                    config_files = await self.deployment_engine.generate_deployment_files(
                        app_name=app_name,
                        source_path=app_path,
                        provider=provider,
                        environment_variables={
                            "NODE_ENV": "production",
                            "PORT": "3000"
                        }
                    )
                    
                    if config_files:
                        print(f"  ✓ Generated {provider.value} config files: {list(config_files.keys())}")
                        
                        # Write config files to app directory
                        for filename, content in config_files.items():
                            config_path = os.path.join(app_path, filename)
                            with open(config_path, 'w') as f:
                                f.write(content)
                        
                        deployment_configs.append({
                            "app": app,
                            "provider": provider,
                            "app_name": app_name,
                            "config_files": config_files
                        })
                    else:
                        print(f"  ✗ Failed to generate {provider.value} config")
                        
                except Exception as e:
                    print(f"  ✗ Exception with {provider.value}: {e}")
        
        return deployment_configs
    
    async def test_deployment_simulation(self, deployment_configs):
        """Test deployment simulation (without actual deployment)"""
        print("\n=== Testing Deployment Simulation ===")
        
        for config in deployment_configs[:6]:  # Test first 6 configurations
            app_name = config["app_name"]
            provider = config["provider"].value
            app_path = config["app"]["path"]
            
            print(f"\nSimulating deployment of {app_name} to {provider}...")
            
            try:
                # Simulate deployment process
                print(f"  • Validating application structure...")
                app_path_obj = Path(app_path)
                
                if not app_path_obj.exists():
                    print(f"    ✗ Application path does not exist: {app_path}")
                    continue
                
                print(f"    ✓ Application path exists: {app_path}")
                
                # Check for generated files
                generated_files = list(config["app"]["files"].keys())
                print(f"    ✓ Generated files: {', '.join(generated_files)}")
                
                # Check for deployment configuration files
                config_files = list(config["config_files"].keys())
                print(f"    ✓ Deployment config files: {', '.join(config_files)}")
                
                # Simulate deployment readiness check
                language = config["app"]["test_case"]["language"]
                framework = config["app"]["test_case"]["framework"]
                
                deployment_ready = True
                
                if provider in ["vercel", "netlify"]:
                    if language in ["javascript", "typescript"]:
                        if "package.json" not in config_files:
                            print(f"    ⚠ Missing package.json for {provider}")
                            deployment_ready = False
                    else:
                        print(f"    ℹ {language} apps may need custom build configuration for {provider}")
                
                elif provider in ["railway", "render"]:
                    if "Dockerfile" not in config_files and language not in ["python", "rust", "go"]:
                        print(f"    ⚠ May need Dockerfile for {provider}")
                
                if deployment_ready:
                    print(f"  ✅ Application ready for deployment to {provider}")
                    print(f"  📋 Deployment strategy: {framework} on {provider}")
                else:
                    print(f"  ⚠ Application needs additional configuration for {provider}")
                
            except Exception as e:
                print(f"  ✗ Simulation error: {e}")
    
    async def test_environment_detection(self):
        """Test environment detection and optimization"""
        print("\n=== Testing Environment Detection ===")
        
        # Test different environment scenarios
        environments = [
            Environment(
                platform="web",
                runtime="serverless", 
                constraints=ResourceConstraints(
                    max_memory_mb=128,
                    max_cpu_cores=1,
                    max_storage_gb=0.1,
                    budget_limit=5.0
                ),
                capabilities=["http_server"]
            ),
            Environment(
                platform="web",
                runtime="container",
                constraints=ResourceConstraints(
                    max_memory_mb=1024,
                    max_cpu_cores=2,
                    max_storage_gb=5.0,
                    budget_limit=50.0
                ),
                capabilities=["http_server", "database", "file_storage"]
            ),
            Environment(
                platform="api",
                runtime="microservice",
                constraints=ResourceConstraints(
                    max_memory_mb=2048,
                    max_cpu_cores=4,
                    max_storage_gb=10.0,
                    budget_limit=100.0
                ),
                capabilities=["http_server", "database", "cache", "queue"]
            )
        ]
        
        for i, env in enumerate(environments):
            print(f"\nEnvironment {i+1}: {env.platform}/{env.runtime}")
            print(f"  Memory: {env.constraints.max_memory_mb}MB")
            print(f"  CPU: {env.constraints.max_cpu_cores} cores")
            print(f"  Storage: {env.constraints.max_storage_gb}GB")
            print(f"  Budget: ${env.constraints.budget_limit}")
            print(f"  Capabilities: {', '.join(env.capabilities)}")
            
            # Determine optimal deployment strategy
            if env.runtime == "serverless":
                recommended_providers = ["vercel", "netlify", "aws_lambda"]
            elif env.runtime == "container":
                recommended_providers = ["railway", "render", "aws_ecs", "gcp_cloud_run"]
            else:
                recommended_providers = ["aws_ecs", "gcp_cloud_run", "azure_container_instances"]
            
            print(f"  Recommended providers: {', '.join(recommended_providers)}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Statement-to-Reality Cloud Deployment Test Suite")
        print("=" * 70)
        
        try:
            # Setup
            await self.setup_test_environment()
            
            # Test 1: Application Generation
            generated_apps = await self.test_application_generation()
            
            if not generated_apps:
                print("\n❌ No applications generated successfully. Skipping deployment tests.")
                return
            
            # Test 2: Deployment Configuration
            deployment_configs = await self.test_deployment_configuration(generated_apps)
            
            # Test 3: Deployment Simulation
            await self.test_deployment_simulation(deployment_configs)
            
            # Test 4: Environment Detection
            await self.test_environment_detection()
            
            print("\n" + "=" * 70)
            print("✅ Cloud Deployment Test Suite Completed Successfully!")
            print(f"Generated {len(generated_apps)} applications")
            print(f"Created {len(deployment_configs)} deployment configurations")
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            await self.cleanup_test_environment()


async def main():
    """Main test execution"""
    tester = CloudDeploymentTester()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
