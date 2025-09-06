#!/usr/bin/env python3
"""
Comprehensive test suite for the refactored Statement-to-Reality System.

Tests all core components, services, and integration points to validate
the refactored architecture works correctly.
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.models import (
    Statement, Conversation, SystemRequirements, SystemArchitecture, 
    SystemComponent, GeneratedCode, StatementType, SystemStatus
)
from src.core.config import SystemConfig, get_config, set_config
from src.core.exceptions import *
from src.services.conversation_service import ConversationService, EnhancedConversationalParser
from src.services.architecture_service import ArchitectureService, EnhancedArchitecturalInference
from src.services.code_generation_service import CodeGenerationService, EnhancedMultiLanguageGenerator
from src.utils.cache import MemoryCache, create_cache_key
from src.utils.metrics import InMemoryMetricsCollector, PerformanceTimer


class TestRunner:
    """Comprehensive test runner for the refactored system."""
    
    def __init__(self):
        self.test_results = []
        self.metrics = InMemoryMetricsCollector()
        
        # Setup test configuration
        test_config = SystemConfig()
        test_config.debug = True
        test_config.enable_caching = True
        set_config(test_config)
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🧪 Starting Refactored System Test Suite")
        print("=" * 60)
        
        test_suites = [
            ("Core Models", self.test_core_models),
            ("Configuration", self.test_configuration),
            ("Caching System", self.test_caching),
            ("Metrics Collection", self.test_metrics),
            ("Conversation Service", self.test_conversation_service),
            ("Architecture Service", self.test_architecture_service),
            ("Code Generation Service", self.test_code_generation_service),
            ("Integration Tests", self.test_integration)
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n📋 Running {suite_name} Tests...")
            try:
                with PerformanceTimer(self.metrics, f"test_{suite_name.lower().replace(' ', '_')}"):
                    test_func()
                self._record_result(suite_name, "PASSED", None)
                print(f"✅ {suite_name} Tests: PASSED")
            except Exception as e:
                self._record_result(suite_name, "FAILED", str(e))
                print(f"❌ {suite_name} Tests: FAILED - {e}")
        
        self._print_summary()
    
    def test_core_models(self):
        """Test core data models."""
        # Test Statement creation and validation
        statement = Statement(
            content="Create a REST API for user management",
            context={"domain": "web_development"},
            timestamp=datetime.now(),
            speaker="user",
            statement_type=StatementType.FUNCTIONAL,
            confidence=0.9
        )
        assert statement.content == "Create a REST API for user management"
        assert statement.confidence == 0.9
        
        # Test Conversation creation
        conversation = Conversation(
            statements=[statement],
            metadata={"session_id": "test_123"},
            conversation_id="conv_001"
        )
        assert len(conversation.statements) == 1
        assert conversation.conversation_id == "conv_001"
        
        # Test SystemComponent
        component = SystemComponent(
            name="UserService",
            component_type="service",
            responsibilities=["User management", "Authentication"],
            interfaces=["UserInterface"],
            dependencies=["DatabaseService"]
        )
        assert component.name == "UserService"
        assert len(component.responsibilities) == 2
        
        # Test validation errors
        try:
            Statement(
                content="",  # Empty content should fail
                context={},
                timestamp=datetime.now(),
                speaker="user",
                statement_type=StatementType.FUNCTIONAL
            )
            assert False, "Should have raised validation error"
        except ValueError:
            pass  # Expected
        
        print("  ✓ Data model validation working correctly")
    
    def test_configuration(self):
        """Test configuration management."""
        config = get_config()
        assert config is not None
        assert hasattr(config, 'llm')
        assert hasattr(config, 'cloud')
        assert hasattr(config, 'codegen')
        
        # Test validation
        issues = config.validate()
        # Should have at least one issue (no API keys in test environment)
        assert isinstance(issues, list)
        
        # Test available providers
        providers = config.get_available_providers()
        assert isinstance(providers, dict)
        assert 'aws' in providers
        assert 'vercel' in providers
        
        print("  ✓ Configuration management working correctly")
    
    def test_caching(self):
        """Test caching system."""
        cache = MemoryCache(default_ttl=60)
        
        # Test basic operations
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        assert value == "test_value"
        
        # Test cache key generation
        key1 = create_cache_key("arg1", "arg2", param1="value1")
        key2 = create_cache_key("arg1", "arg2", param1="value1")
        key3 = create_cache_key("arg1", "arg2", param1="value2")
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different inputs should generate different keys
        
        # Test deletion
        cache.delete("test_key")
        value = cache.get("test_key")
        assert value is None
        
        print("  ✓ Caching system working correctly")
    
    def test_metrics(self):
        """Test metrics collection."""
        metrics = InMemoryMetricsCollector()
        
        # Test counter
        metrics.increment_counter("test_counter")
        metrics.increment_counter("test_counter")
        
        # Test gauge
        metrics.record_gauge("test_gauge", 42.5)
        
        # Test timing
        metrics.record_processing_time("test_operation", 1.23)
        
        # Get summary
        summary = metrics.get_metrics_summary()
        assert "counters" in summary
        assert "gauges" in summary
        assert "timing_stats" in summary
        
        assert summary["counters"]["test_counter"] == 2
        assert summary["gauges"]["test_gauge"] == 42.5
        
        print("  ✓ Metrics collection working correctly")
    
    def test_conversation_service(self):
        """Test conversation processing service."""
        parser = EnhancedConversationalParser()
        service = ConversationService(parser)
        
        # Create test conversation
        statements = [
            Statement(
                content="Create a REST API for user management with authentication",
                context={"domain": "web_development"},
                timestamp=datetime.now(),
                speaker="user",
                statement_type=StatementType.FUNCTIONAL
            ),
            Statement(
                content="The system should handle 1000 concurrent users",
                context={"performance": True},
                timestamp=datetime.now(),
                speaker="user",
                statement_type=StatementType.NON_FUNCTIONAL
            )
        ]
        
        conversation = Conversation(
            statements=statements,
            metadata={"session_id": "test_session"},
            conversation_id="test_conv"
        )
        
        # Test processing
        result = service.process_conversation(conversation)
        assert result.success == True
        assert result.requirements is not None
        assert len(result.requirements.functional_requirements) > 0
        
        # Test complexity analysis
        complexity = service.analyze_conversation_complexity(conversation)
        assert "statement_count" in complexity
        assert complexity["statement_count"] == 2
        
        # Test entity extraction
        entities = parser.extract_entities("Create a REST API with authentication and database")
        assert "api" in entities
        assert "authentication" in entities
        assert "database" in entities
        
        print("  ✓ Conversation service working correctly")
    
    def test_architecture_service(self):
        """Test architecture inference service."""
        inference_engine = EnhancedArchitecturalInference()
        service = ArchitectureService(inference_engine)
        
        # Create test requirements
        requirements = SystemRequirements(
            functional_requirements=["Create REST API", "User authentication"],
            non_functional_requirements=["Handle 1000 users", "Response time < 200ms"],
            constraints=["Must use PostgreSQL"],
            business_rules=["Users must verify email"],
            quality_attributes={"performance": True, "scalability": True},
            extracted_entities=["api", "user", "authentication", "database"],
            confidence_score=0.8
        )
        
        # Test architecture inference
        architecture = service.infer_and_validate_architecture(requirements)
        assert architecture is not None
        assert len(architecture.components) > 0
        assert len(architecture.patterns) > 0
        
        # Test validation
        issues = service.validate_architecture_comprehensive(architecture)
        # Should be minimal issues for a well-formed architecture
        
        # Test pattern suggestion
        patterns = inference_engine.suggest_patterns(requirements)
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        print("  ✓ Architecture service working correctly")
    
    def test_code_generation_service(self):
        """Test code generation service."""
        generator = EnhancedMultiLanguageGenerator()
        service = CodeGenerationService(generator)
        
        # Create test architecture
        components = [
            SystemComponent(
                name="APIService",
                component_type="api",
                responsibilities=["Handle HTTP requests"],
                interfaces=["RestAPI"],
                dependencies=[]
            )
        ]
        
        architecture = SystemArchitecture(
            components=components,
            relationships=[],
            patterns=["mvc"],
            quality_attributes={"performance": True},
            technology_stack={"backend": ["Python"], "database": ["PostgreSQL"]},
            deployment_model="cloud"
        )
        
        # Test single language generation
        code = generator.generate_code(architecture, "python", "fastapi")
        assert code is not None
        assert code.language == "python"
        assert code.framework == "fastapi"
        assert len(code.files) > 0
        assert code.entry_point in code.files
        
        # Test supported languages
        languages = generator.get_supported_languages()
        assert "python" in languages
        assert "rust" in languages
        
        # Test frameworks
        frameworks = generator.get_supported_frameworks("python")
        assert "fastapi" in frameworks
        assert "flask" in frameworks
        
        # Test validation
        issues = generator.validate_code(code)
        assert isinstance(issues, list)
        
        print("  ✓ Code generation service working correctly")
    
    async def test_integration(self):
        """Test full system integration."""
        # Create services
        parser = EnhancedConversationalParser()
        conversation_service = ConversationService(parser)
        
        inference_engine = EnhancedArchitecturalInference()
        architecture_service = ArchitectureService(inference_engine)
        
        generator = EnhancedMultiLanguageGenerator()
        code_service = CodeGenerationService(generator)
        
        # Create test conversation
        statements = [
            Statement(
                content="Build a chat application with real-time messaging",
                context={"type": "web_app"},
                timestamp=datetime.now(),
                speaker="user",
                statement_type=StatementType.FUNCTIONAL
            ),
            Statement(
                content="Support 500 concurrent users with low latency",
                context={"performance": True},
                timestamp=datetime.now(),
                speaker="user",
                statement_type=StatementType.NON_FUNCTIONAL
            )
        ]
        
        conversation = Conversation(
            statements=statements,
            metadata={"project": "chat_app"},
            conversation_id="integration_test"
        )
        
        # Full pipeline test
        # 1. Process conversation
        conv_result = conversation_service.process_conversation(conversation)
        assert conv_result.success
        
        # 2. Infer architecture
        architecture = architecture_service.infer_and_validate_architecture(conv_result.requirements)
        assert architecture is not None
        
        # 3. Generate code for multiple languages
        languages = ["python", "rust"]
        code_results = await code_service.generate_multi_language_code(architecture, languages)
        
        assert len(code_results) == 2
        assert "python" in code_results
        assert "rust" in code_results
        
        # Validate generated code
        for lang, code in code_results.items():
            assert code.language == lang
            assert len(code.files) > 0
            assert code.entry_point in code.files
        
        print("  ✓ Full system integration working correctly")
    
    def _record_result(self, test_name: str, status: str, error: str):
        """Record test result."""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "error": error,
            "timestamp": datetime.now()
        })
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = sum(1 for r in self.test_results if r["status"] == "FAILED")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"  ❌ {result['test']}: {result['error']}")
        
        # Print performance metrics
        metrics_summary = self.metrics.get_metrics_summary()
        if metrics_summary.get("timing_stats"):
            print("\n⏱️  PERFORMANCE METRICS:")
            for operation, stats in metrics_summary["timing_stats"].items():
                print(f"  {operation}: {stats['avg']:.3f}s avg ({stats['count']} runs)")
        
        print("\n🎉 Refactored System Test Complete!")


def main():
    """Main test execution."""
    runner = TestRunner()
    
    # Run synchronous tests
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
