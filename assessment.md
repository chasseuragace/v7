#!/usr/bin/env python3
"""
Test case for the ConversationService in the Statement-to-Reality System.
Validates parsing of natural language statements into system requirements.
"""

from datetime import datetime
from src.core.models import Statement, Conversation, StatementType
from src.services.conversation_service import ConversationService, EnhancedConversationalParser

def test_conversation_service_parse():
    """Test ConversationService for parsing a simple statement."""
    # Initialize parser and service
    parser = EnhancedConversationalParser()
    service = ConversationService(parser)

    # Create a test statement
    statement_content = "Create a REST API for user management with authentication"
    statement = Statement(
        content=statement_content,
        context={"domain": "web_development"},
        timestamp=datetime.now(),
        speaker="user",
        statement_type=StatementType.FUNCTIONAL
    )

    # Create a conversation
    conversation = Conversation(
        statements=[statement],
        metadata={"session_id": "test_session_001"},
        conversation_id="test_conv_001"
    )

    # Process the conversation
    result = service.process_conversation(conversation)

    # Validate results
    assert result.success, "Conversation processing should succeed"
    assert result.requirements is not None, "Requirements should be generated"
    assert len(result.requirements.functional_requirements) > 0, "Functional requirements should be extracted"
    
    # Check if REST API requirement is present (case-insensitive search)
    func_reqs_text = ' '.join(result.requirements.functional_requirements).lower()
    assert "rest" in func_reqs_text or "api" in func_reqs_text, "REST API requirement should be present"
    assert "authentication" in result.requirements.extracted_entities, "Authentication entity should be extracted"

    # Test complexity analysis
    complexity = service.analyze_conversation_complexity(conversation)
    assert complexity["statement_count"] == 1, "Should count one statement"

    print("✓ ConversationService parsing test passed")
    return result

if __name__ == "__main__":
    test_conversation_service_parse()