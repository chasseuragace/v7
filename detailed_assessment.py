#!/usr/bin/env python3
"""
Detailed assessment of the ConversationService to verify all functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from src.core.models import Statement, Conversation, StatementType
from src.services.conversation_service import ConversationService, EnhancedConversationalParser

def detailed_conversation_assessment():
    """Comprehensive test of ConversationService functionality."""
    print("🔍 Running Detailed ConversationService Assessment")
    print("=" * 50)
    
    # Initialize parser and service
    parser = EnhancedConversationalParser()
    service = ConversationService(parser)
    
    # Test 1: Basic statement processing
    print("\n1. Testing Basic Statement Processing...")
    statement = Statement(
        content="Create a REST API for user management with authentication",
        context={"domain": "web_development"},
        timestamp=datetime.now(),
        speaker="user",
        statement_type=StatementType.FUNCTIONAL
    )
    
    conversation = Conversation(
        statements=[statement],
        metadata={"session_id": "test_session"},
        conversation_id="test_conv"
    )
    
    result = service.process_conversation(conversation)
    
    print(f"   ✓ Processing success: {result.success}")
    print(f"   ✓ Requirements generated: {result.requirements is not None}")
    print(f"   ✓ Functional requirements count: {len(result.requirements.functional_requirements)}")
    print(f"   ✓ Extracted entities: {result.requirements.extracted_entities}")
    
    # Test 2: Entity extraction validation
    print("\n2. Testing Entity Extraction...")
    test_text = "Create a REST API with authentication, database, and payment processing"
    entities = parser.extract_entities(test_text)
    print(f"   ✓ Entities from '{test_text}': {entities}")
    
    expected_entities = ['api', 'authentication', 'database', 'payment']
    found_entities = [e for e in expected_entities if e in entities]
    print(f"   ✓ Expected entities found: {found_entities}")
    
    # Test 3: Statement classification
    print("\n3. Testing Statement Classification...")
    classification = parser.classify_statement(statement)
    print(f"   ✓ Statement classification: {classification}")
    
    # Test 4: Complex conversation
    print("\n4. Testing Complex Multi-Statement Conversation...")
    complex_statements = [
        Statement(
            content="Build a chat application with real-time messaging",
            context={"type": "web_app"},
            timestamp=datetime.now(),
            speaker="user",
            statement_type=StatementType.FUNCTIONAL
        ),
        Statement(
            content="The system must handle 1000 concurrent users",
            context={"performance": True},
            timestamp=datetime.now(),
            speaker="user",
            statement_type=StatementType.NON_FUNCTIONAL
        ),
        Statement(
            content="Use WebSocket for real-time communication",
            context={"technical": True},
            timestamp=datetime.now(),
            speaker="user",
            statement_type=StatementType.CONSTRAINT
        )
    ]
    
    complex_conversation = Conversation(
        statements=complex_statements,
        metadata={"project": "chat_app"},
        conversation_id="complex_test"
    )
    
    complex_result = service.process_conversation(complex_conversation)
    print(f"   ✓ Complex processing success: {complex_result.success}")
    print(f"   ✓ Functional requirements: {len(complex_result.requirements.functional_requirements)}")
    print(f"   ✓ Non-functional requirements: {len(complex_result.requirements.non_functional_requirements)}")
    print(f"   ✓ Constraints: {len(complex_result.requirements.constraints)}")
    
    # Test 5: Complexity analysis
    print("\n5. Testing Complexity Analysis...")
    complexity = service.analyze_conversation_complexity(complex_conversation)
    print(f"   ✓ Statement count: {complexity['statement_count']}")
    print(f"   ✓ Statement types: {complexity['statement_types']}")
    print(f"   ✓ Complexity score: {complexity['complexity_score']:.2f}")
    print(f"   ✓ Estimated processing time: {complexity['estimated_processing_time']:.2f}s")
    
    # Test 6: Key concepts extraction
    print("\n6. Testing Key Concepts Extraction...")
    concepts = service.extract_key_concepts(complex_conversation)
    print(f"   ✓ Key concepts: {concepts}")
    
    # Test 7: Error handling
    print("\n7. Testing Error Handling...")
    try:
        empty_conversation = Conversation(
            statements=[],
            metadata={},
            conversation_id="empty_test"
        )
        error_result = service.process_conversation(empty_conversation)
        print(f"   ✓ Empty conversation handled: {not error_result.success}")
        print(f"   ✓ Error recorded: {len(error_result.errors) > 0}")
    except Exception as e:
        print(f"   ✓ Exception caught: {type(e).__name__}")
    
    print("\n" + "=" * 50)
    print("📊 DETAILED ASSESSMENT SUMMARY")
    print("=" * 50)
    
    # Verify all core functionality
    checks = [
        ("Basic statement processing", result.success),
        ("Requirements extraction", len(result.requirements.functional_requirements) > 0),
        ("Entity extraction", len(entities) > 0),
        ("Statement classification", classification is not None),
        ("Complex conversation handling", complex_result.success),
        ("Complexity analysis", complexity['statement_count'] == 3),
        ("Key concepts extraction", len(concepts) > 0)
    ]
    
    passed = sum(1 for _, check in checks if check)
    total = len(checks)
    
    print(f"\nChecks Passed: {passed}/{total}")
    for check_name, passed_check in checks:
        status = "✅ PASS" if passed_check else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    success_rate = (passed / total) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ConversationService is FULLY FUNCTIONAL!")
    else:
        print("⚠️  ConversationService has issues that need attention.")
    
    return success_rate == 100

if __name__ == "__main__":
    detailed_conversation_assessment()
