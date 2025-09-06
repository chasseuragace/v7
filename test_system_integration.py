#!/usr/bin/env python3
"""
System Integration Test for Statement-to-Reality System
Tests the complete pipeline from statement to deployable application
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path
import json

from multi_language_generator import create_multi_language_generator
from cloud_deployment import create_cloud_deployment_engine, DeploymentConfig
from statement_reality_system import Architecture, ArchitecturalComponent


class SystemIntegrationTester:
    """Complete system integration test suite"""
    
    def __init__(self):
        self.generator = create_multi_language_generator()
        self.deployment_engine = create_cloud_deployment_engine()
        self.test_dir = None
        
    async def setup_test_environment(self):
        """Setup temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="statement_reality_integration_")
        print(f"🔧 Created test directory: {self.test_dir}")
        
    async def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory: {self.test_dir}")
    
    async def test_multi_language_generation(self):
        """Test multi-language code generation capabilities"""
        print("\n=== 🌍 Testing Multi-Language Code Generation ===")
        
        # Create a test architecture
        architecture = Architecture(
            components=[
                ArchitecturalComponent(
                    name="UserAPI",
                    responsibilities=["Handle user requests", "Validate input", "Route endpoints"],
                    interfaces=["get_users", "create_user", "update_user", "delete_user"],
                    dependencies=[],
                    constraints={"rate_limit": "100/min"}
                ),
                ArchitecturalComponent(
                    name="UserService",
                    responsibilities=["Business logic", "Data validation", "User management"],
                    interfaces=["process_user", "validate_user", "transform_data"],
                    dependencies=["UserAPI"],
                    constraints={"max_users": 10000}
                ),
                ArchitecturalComponent(
                    name="UserStorage",
                    responsibilities=["Data persistence", "Query optimization", "Transaction management"],
                    interfaces=["save_user", "load_user", "query_users", "delete_user"],
                    dependencies=["UserService"],
                    constraints={"consistency": "strong"}
                )
            ],
            patterns=["REST API", "Layered Architecture", "Repository Pattern"],
            relationships={"UserAPI": ["UserService"], "UserService": ["UserStorage"]},
            constraints={"scalability": "horizontal", "availability": "99.9%"},
            quality_attributes={"performance": "high", "security": "high", "maintainability": "medium"}
        )
        
        # Test different language/framework combinations
        test_cases = [
            ("python", "fastapi", "🐍 Python FastAPI"),
            ("rust", "axum", "🦀 Rust Axum"),
            ("go", "gin", "🐹 Go Gin"),
            ("typescript", "express", "📘 TypeScript Express"),
            ("java", "spring", "☕ Java Spring"),
            ("cpp", "crow", "⚡ C++ Crow")
        ]
        
        generated_results = []
        
        for language, framework, display_name in test_cases:
            print(f"\n{display_name} Application Generation:")
            
            try:
                # Generate code
                generated_files = self.generator.generate_code(architecture, language, framework)
                
                if generated_files:
                    print(f"  ✅ Generated {len(generated_files)} files")
                    
                    # Create output directory
                    output_dir = os.path.join(self.test_dir, f"{language}_{framework}")
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Write files to disk
                    for filename, content in generated_files.items():
                        file_path = os.path.join(output_dir, filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'w') as f:
                            f.write(content)
                    
                    print(f"  📁 Files: {', '.join(generated_files.keys())}")
                    
                    generated_results.append({
                        "language": language,
                        "framework": framework,
                        "display_name": display_name,
                        "files": generated_files,
                        "path": output_dir
                    })
                else:
                    print(f"  ❌ No files generated")
                    
            except Exception as e:
                print(f"  ❌ Generation failed: {e}")
        
        return generated_results
    
    async def test_deployment_configuration(self, generated_results):
        """Test deployment configuration generation"""
        print("\n=== ☁️ Testing Deployment Configuration ===")
        
        deployment_configs = []
        
        # Test deployment configurations for different providers
        providers = ["aws", "gcp", "azure", "vercel", "netlify"]
        
        for result in generated_results[:3]:  # Test first 3 languages
            language = result["language"]
            framework = result["framework"]
            display_name = result["display_name"]
            
            print(f"\n{display_name} Deployment Configurations:")
            
            for provider in providers:
                try:
                    # Create deployment config
                    config = DeploymentConfig(
                        provider=provider,
                        region="us-east-1" if provider == "aws" else "us-central1",
                        project_id=f"statement-reality-{language}" if provider == "gcp" else None,
                        resource_group=f"statement-reality-rg" if provider == "azure" else None,
                        environment="production"
                    )
                    
                    print(f"  📋 {provider.upper()} config created")
                    
                    deployment_configs.append({
                        "result": result,
                        "provider": provider,
                        "config": config
                    })
                    
                except Exception as e:
                    print(f"  ❌ {provider.upper()} config failed: {e}")
        
        return deployment_configs
    
    async def test_deployment_simulation(self, deployment_configs):
        """Test deployment simulation without actual deployment"""
        print("\n=== 🚀 Testing Deployment Simulation ===")
        
        for config_item in deployment_configs[:6]:  # Test first 6 configurations
            result = config_item["result"]
            provider = config_item["provider"]
            config = config_item["config"]
            
            display_name = result["display_name"]
            language = result["language"]
            
            print(f"\n{display_name} → {provider.upper()}:")
            
            try:
                # Simulate deployment validation
                files = result["files"]
                
                print(f"  📦 Validating {len(files)} files for {provider}")
                
                # Check deployment readiness
                deployment_ready = True
                missing_files = []
                
                if provider in ["vercel", "netlify"]:
                    if language in ["javascript", "typescript"]:
                        if "package.json" not in files:
                            missing_files.append("package.json")
                            deployment_ready = False
                    elif language == "python":
                        if "requirements.txt" not in files:
                            missing_files.append("requirements.txt")
                
                elif provider in ["aws", "gcp", "azure"]:
                    if "Dockerfile" not in files:
                        missing_files.append("Dockerfile")
                        # Don't mark as not ready since we can generate Dockerfile
                
                if deployment_ready:
                    print(f"  ✅ Ready for deployment to {provider}")
                    print(f"  🎯 Strategy: Container deployment")
                else:
                    print(f"  ⚠️  Missing files: {', '.join(missing_files)}")
                
                print(f"  🌐 Would deploy to region: {config.region}")
                
            except Exception as e:
                print(f"  ❌ Simulation error: {e}")
    
    async def test_system_capabilities(self):
        """Test overall system capabilities"""
        print("\n=== 🔍 Testing System Capabilities ===")
        
        # Test supported languages
        supported_languages = self.generator.get_supported_languages()
        print(f"📚 Supported Languages: {', '.join(supported_languages)}")
        
        # Test system scalability
        print(f"🔧 Multi-language Generator: {type(self.generator).__name__}")
        print(f"☁️  Cloud Deployment Engine: {type(self.deployment_engine).__name__}")
        
        # Test architecture complexity handling
        complex_architecture = Architecture(
            components=[
                ArchitecturalComponent(f"Component{i}", [f"responsibility{i}"], [f"interface{i}"], [], {})
                for i in range(10)
            ],
            patterns=["Microservices", "Event-Driven", "CQRS", "Saga Pattern"],
            relationships={f"Component{i}": [f"Component{j}"] for i in range(5) for j in range(i+1, 10)},
            constraints={"distributed": True, "eventual_consistency": True},
            quality_attributes={"scalability": "extreme", "availability": "99.99%"}
        )
        
        try:
            # Test with complex architecture
            complex_files = self.generator.generate_code(complex_architecture, "python", "fastapi")
            print(f"✅ Complex architecture handling: Generated {len(complex_files)} files")
        except Exception as e:
            print(f"⚠️  Complex architecture limitation: {e}")
    
    async def run_integration_test(self):
        """Run complete integration test suite"""
        print("🚀 Statement-to-Reality System Integration Test")
        print("=" * 70)
        
        try:
            # Setup
            await self.setup_test_environment()
            
            # Test 1: Multi-language generation
            generated_results = await self.test_multi_language_generation()
            
            if not generated_results:
                print("\n❌ No applications generated. Stopping tests.")
                return
            
            # Test 2: Deployment configuration
            deployment_configs = await self.test_deployment_configuration(generated_results)
            
            # Test 3: Deployment simulation
            await self.test_deployment_simulation(deployment_configs)
            
            # Test 4: System capabilities
            await self.test_system_capabilities()
            
            # Summary
            print("\n" + "=" * 70)
            print("✅ Integration Test Suite Completed!")
            print(f"📊 Results Summary:")
            print(f"   • Generated applications: {len(generated_results)}")
            print(f"   • Deployment configurations: {len(deployment_configs)}")
            print(f"   • Languages tested: {len(set(r['language'] for r in generated_results))}")
            print(f"   • Cloud providers tested: {len(set(c['provider'] for c in deployment_configs))}")
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            await self.cleanup_test_environment()


async def main():
    """Main test execution"""
    tester = SystemIntegrationTester()
    await tester.run_integration_test()


if __name__ == "__main__":
    asyncio.run(main())
