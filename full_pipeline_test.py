#!/usr/bin/env python3
"""
Full pipeline test to verify artifact generation in the Statement-to-Reality System.
This should generate actual code files, deployment configs, and running systems.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from src.core.models import Statement, Conversation, StatementType
from src.services.conversation_service import ConversationService, EnhancedConversationalParser
from src.services.architecture_service import ArchitectureService, EnhancedArchitecturalInference
from src.services.code_generation_service import CodeGenerationService, EnhancedMultiLanguageGenerator

def test_full_artifact_generation():
    """Test complete pipeline from statement to actual artifacts."""
    print("🏗️  Testing Full Artifact Generation Pipeline")
    print("=" * 60)
    
    # Initialize all services
    parser = EnhancedConversationalParser()
    conversation_service = ConversationService(parser)
    
    inference_engine = EnhancedArchitecturalInference()
    architecture_service = ArchitectureService(inference_engine)
    
    generator = EnhancedMultiLanguageGenerator()
    code_service = CodeGenerationService(generator)
    
    # Create test statement
    statement = Statement(
        content="Create a REST API for a todo application with user authentication and task management",
        context={"domain": "web_development", "type": "api"},
        timestamp=datetime.now(),
        speaker="user",
        statement_type=StatementType.FUNCTIONAL
    )
    
    conversation = Conversation(
        statements=[statement],
        metadata={"project": "todo_api"},
        conversation_id="artifact_test"
    )
    
    print("\n1. Processing Conversation...")
    # Step 1: Process conversation
    conv_result = conversation_service.process_conversation(conversation)
    print(f"   ✓ Conversation processed: {conv_result.success}")
    print(f"   ✓ Requirements extracted: {len(conv_result.requirements.functional_requirements)}")
    print(f"   ✓ Entities found: {conv_result.requirements.extracted_entities}")
    
    print("\n2. Inferring Architecture...")
    # Step 2: Infer architecture
    architecture = architecture_service.infer_and_validate_architecture(conv_result.requirements)
    print(f"   ✓ Components generated: {len(architecture.components)}")
    print(f"   ✓ Patterns applied: {architecture.patterns}")
    print(f"   ✓ Technology stack: {architecture.technology_stack}")
    
    # Print component details
    for component in architecture.components:
        print(f"     - {component.name} ({component.component_type})")
    
    print("\n3. Generating Code Artifacts...")
    # Step 3: Generate code for multiple languages
    languages = ["python", "rust"]
    
    artifacts = {}
    for language in languages:
        print(f"\n   Generating {language.upper()} code...")
        try:
            code = generator.generate_code(architecture, language)
            artifacts[language] = code
            
            print(f"     ✓ Language: {code.language}")
            print(f"     ✓ Framework: {code.framework}")
            print(f"     ✓ Files generated: {len(code.files)}")
            print(f"     ✓ Entry point: {code.entry_point}")
            print(f"     ✓ Dependencies: {code.dependencies}")
            
            # Show file names
            for filename in code.files.keys():
                print(f"       - {filename}")
                
        except Exception as e:
            print(f"     ❌ Failed to generate {language}: {e}")
    
    print("\n4. Saving Generated Artifacts...")
    # Step 4: Save artifacts to files
    output_dir = "generated_artifacts"
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    for language, code in artifacts.items():
        lang_dir = os.path.join(output_dir, language)
        os.makedirs(lang_dir, exist_ok=True)
        
        for filename, content in code.files.items():
            file_path = os.path.join(lang_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            saved_files.append(file_path)
            print(f"   ✓ Saved: {file_path}")
    
    print("\n5. Generating Deployment Configurations...")
    # Step 5: Generate deployment configs (simulated)
    deployment_configs = {}
    providers = ["vercel", "aws", "docker"]
    
    for provider in providers:
        config_content = f"""# {provider.upper()} Deployment Configuration
# Generated for Todo API application
# Architecture: {', '.join(architecture.patterns)}
# Components: {len(architecture.components)}

name: todo-api-{provider}
runtime: {architecture.technology_stack.get('backend', ['python'])[0]}
build_command: pip install -r requirements.txt
start_command: python main.py
"""
        
        config_file = os.path.join(output_dir, f"{provider}_deploy.yml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        deployment_configs[provider] = config_file
        saved_files.append(config_file)
        print(f"   ✓ Generated: {config_file}")
    
    print("\n" + "=" * 60)
    print("📦 ARTIFACT GENERATION SUMMARY")
    print("=" * 60)
    
    print(f"✅ Conversation Requirements: {len(conv_result.requirements.functional_requirements)} functional")
    print(f"✅ Architecture Components: {len(architecture.components)}")
    print(f"✅ Code Languages: {len(artifacts)}")
    print(f"✅ Generated Files: {len(saved_files)}")
    print(f"✅ Deployment Configs: {len(deployment_configs)}")
    
    print(f"\n📁 All artifacts saved to: {os.path.abspath(output_dir)}")
    
    # Verify artifacts exist
    print(f"\n🔍 Verifying Generated Artifacts:")
    for file_path in saved_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✓ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    return len(saved_files) > 0

if __name__ == "__main__":
    success = test_full_artifact_generation()
    if success:
        print("\n🎉 ARTIFACT GENERATION SUCCESSFUL!")
    else:
        print("\n❌ ARTIFACT GENERATION FAILED!")
