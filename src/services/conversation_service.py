"""
Refactored conversation processing service.

This service handles all conversation-related operations with improved
error handling, logging, and performance optimizations.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from src.core.models import (
    Conversation, Statement, SystemRequirements, StatementType, ProcessingResult
)
from src.core.exceptions import ConversationProcessingError, StatementParsingError
from src.core.logging import LoggerMixin, log_processing_time
from src.core.config import get_config
from src.interfaces.base import ConversationalParser


class ConversationService(LoggerMixin):
    """Service for processing conversations with enhanced capabilities."""
    
    def __init__(self, parser: ConversationalParser):
        self.parser = parser
        self.config = get_config()
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_generations)
    
    @log_processing_time
    def process_conversation(self, conversation: Conversation) -> ProcessingResult:
        """
        Process a conversation with comprehensive error handling.
        
        Args:
            conversation: Conversation to process
            
        Returns:
            ProcessingResult with requirements and metadata
        """
        start_time = datetime.now()
        result = ProcessingResult(
            conversation=conversation,
            requirements=SystemRequirements([], [], [], [], {}, []),
            architecture=None,
            generated_code={},
            deployment_configs={}
        )
        
        try:
            self.logger.info(f"Processing conversation {conversation.conversation_id}")
            
            # Validate conversation
            self._validate_conversation(conversation)
            
            # Parse statements
            requirements = self.parser.parse_statements(conversation)
            result.requirements = requirements
            
            # Add processing metadata
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            result.metadata = {
                "statement_count": len(conversation.statements),
                "processing_time": processing_time,
                "parser_type": type(self.parser).__name__
            }
            
            self.logger.info(f"Successfully processed conversation in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process conversation: {e}")
            result.add_error(f"Conversation processing failed: {str(e)}")
            return result
    
    async def process_conversation_async(self, conversation: Conversation) -> ProcessingResult:
        """Process conversation asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.process_conversation, conversation)
    
    def _validate_conversation(self, conversation: Conversation) -> None:
        """Validate conversation structure and content."""
        if not conversation.statements:
            raise ConversationProcessingError("Conversation has no statements")
        
        if len(conversation.statements) > 1000:  # Reasonable limit
            raise ConversationProcessingError("Conversation too long (>1000 statements)")
        
        # Validate individual statements
        for i, statement in enumerate(conversation.statements):
            try:
                self._validate_statement(statement)
            except Exception as e:
                raise ConversationProcessingError(f"Invalid statement at index {i}: {e}")
    
    def _validate_statement(self, statement: Statement) -> None:
        """Validate individual statement."""
        if not statement.content.strip():
            raise StatementParsingError("Statement content is empty")
        
        if len(statement.content) > 10000:  # Reasonable limit
            raise StatementParsingError("Statement too long (>10000 characters)")
        
        # Check for required fields
        required_fields = ['content', 'context', 'timestamp', 'speaker', 'statement_type']
        for field in required_fields:
            if not hasattr(statement, field) or getattr(statement, field) is None:
                raise StatementParsingError(f"Statement missing required field: {field}")
    
    def analyze_conversation_complexity(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze conversation complexity for processing optimization."""
        statement_types = {}
        total_length = 0
        
        for statement in conversation.statements:
            stmt_type = statement.statement_type.value
            statement_types[stmt_type] = statement_types.get(stmt_type, 0) + 1
            total_length += len(statement.content)
        
        complexity_score = self._calculate_complexity_score(conversation)
        
        return {
            "statement_count": len(conversation.statements),
            "statement_types": statement_types,
            "total_length": total_length,
            "average_length": total_length / len(conversation.statements),
            "complexity_score": complexity_score,
            "estimated_processing_time": self._estimate_processing_time(complexity_score)
        }
    
    def _calculate_complexity_score(self, conversation: Conversation) -> float:
        """Calculate complexity score based on conversation characteristics."""
        score = 0.0
        
        # Base score from statement count
        score += len(conversation.statements) * 0.1
        
        # Add complexity for different statement types
        type_weights = {
            StatementType.FUNCTIONAL: 1.0,
            StatementType.NON_FUNCTIONAL: 1.5,
            StatementType.CONSTRAINT: 2.0,
            StatementType.BUSINESS_RULE: 1.2,
            StatementType.EVOLUTION: 2.5
        }
        
        for statement in conversation.statements:
            weight = type_weights.get(statement.statement_type, 1.0)
            score += weight
        
        # Normalize to 0-10 scale
        return min(score / len(conversation.statements), 10.0)
    
    def _estimate_processing_time(self, complexity_score: float) -> float:
        """Estimate processing time based on complexity score."""
        base_time = 5.0  # Base 5 seconds
        complexity_multiplier = 1 + (complexity_score / 10)
        return base_time * complexity_multiplier
    
    def extract_key_concepts(self, conversation: Conversation) -> List[str]:
        """Extract key concepts from conversation for caching and optimization."""
        concepts = set()
        
        for statement in conversation.statements:
            # Extract entities using the parser
            entities = self.parser.extract_entities(statement.content)
            concepts.update(entities)
        
        return list(concepts)
    
    def get_conversation_summary(self, conversation: Conversation) -> Dict[str, Any]:
        """Generate a comprehensive conversation summary."""
        analysis = self.analyze_conversation_complexity(conversation)
        concepts = self.extract_key_concepts(conversation)
        
        return {
            "conversation_id": conversation.conversation_id,
            "created_at": conversation.created_at.isoformat(),
            "statement_analysis": analysis,
            "key_concepts": concepts[:20],  # Top 20 concepts
            "metadata": conversation.metadata
        }


class EnhancedConversationalParser(ConversationalParser, LoggerMixin):
    """Enhanced conversational parser with improved capabilities."""
    
    def __init__(self):
        self.config = get_config()
        self._entity_cache = {}
        self._classification_cache = {}
    
    def parse_statements(self, conversation: Conversation) -> SystemRequirements:
        """Parse conversation statements into structured requirements."""
        self.logger.info(f"Parsing {len(conversation.statements)} statements")
        
        functional_reqs = []
        non_functional_reqs = []
        constraints = []
        business_rules = []
        entities = set()
        
        for statement in conversation.statements:
            try:
                # Extract requirements based on statement type
                if statement.statement_type == StatementType.FUNCTIONAL:
                    functional_reqs.extend(self._extract_functional_requirements(statement))
                elif statement.statement_type == StatementType.NON_FUNCTIONAL:
                    non_functional_reqs.extend(self._extract_non_functional_requirements(statement))
                elif statement.statement_type == StatementType.CONSTRAINT:
                    constraints.extend(self._extract_constraints(statement))
                elif statement.statement_type == StatementType.BUSINESS_RULE:
                    business_rules.extend(self._extract_business_rules(statement))
                
                # Extract entities
                statement_entities = self.extract_entities(statement.content)
                entities.update(statement_entities)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse statement: {e}")
                continue
        
        # Calculate confidence score
        confidence = self._calculate_parsing_confidence(conversation)
        
        return SystemRequirements(
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            constraints=constraints,
            business_rules=business_rules,
            quality_attributes=self._extract_quality_attributes(conversation),
            extracted_entities=list(entities),
            confidence_score=confidence
        )
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities from text with caching."""
        if text in self._entity_cache:
            return self._entity_cache[text]
        
        # Simple entity extraction (can be enhanced with NLP libraries)
        entities = []
        
        # Extract common technical entities
        technical_keywords = [
            'api', 'database', 'user', 'authentication', 'authorization',
            'payment', 'notification', 'email', 'sms', 'file', 'upload',
            'download', 'search', 'filter', 'sort', 'pagination', 'cache',
            'session', 'cookie', 'token', 'jwt', 'oauth', 'ssl', 'https',
            'rest', 'graphql', 'websocket', 'microservice', 'container',
            'docker', 'kubernetes', 'aws', 'gcp', 'azure'
        ]
        
        text_lower = text.lower()
        for keyword in technical_keywords:
            if keyword in text_lower:
                entities.append(keyword)
        
        # Cache result
        self._entity_cache[text] = entities
        return entities
    
    def classify_statement(self, statement: Statement) -> str:
        """Classify statement with caching."""
        cache_key = f"{statement.content}_{statement.statement_type.value}"
        if cache_key in self._classification_cache:
            return self._classification_cache[cache_key]
        
        # Simple classification based on keywords
        content_lower = statement.content.lower()
        
        if any(word in content_lower for word in ['create', 'build', 'implement', 'develop']):
            classification = 'implementation'
        elif any(word in content_lower for word in ['performance', 'speed', 'scalability']):
            classification = 'performance'
        elif any(word in content_lower for word in ['security', 'authentication', 'authorization']):
            classification = 'security'
        elif any(word in content_lower for word in ['ui', 'interface', 'design', 'user experience']):
            classification = 'interface'
        else:
            classification = 'general'
        
        # Cache result
        self._classification_cache[cache_key] = classification
        return classification
    
    def _extract_functional_requirements(self, statement: Statement) -> List[str]:
        """Extract functional requirements from statement."""
        content = statement.content
        requirements = []
        
        # Look for action verbs and objects
        action_patterns = [
            'create', 'build', 'implement', 'develop', 'add', 'remove',
            'update', 'delete', 'manage', 'handle', 'process', 'generate'
        ]
        
        content_lower = content.lower()
        for pattern in action_patterns:
            if pattern in content_lower:
                # Extract the requirement around the action
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        requirements.append(sentence.strip())
        
        return requirements if requirements else [content]
    
    def _extract_non_functional_requirements(self, statement: Statement) -> List[str]:
        """Extract non-functional requirements from statement."""
        content = statement.content
        requirements = []
        
        # Look for quality attributes
        quality_patterns = [
            'performance', 'scalability', 'security', 'reliability',
            'availability', 'usability', 'maintainability', 'portability'
        ]
        
        content_lower = content.lower()
        for pattern in quality_patterns:
            if pattern in content_lower:
                requirements.append(f"{pattern.title()}: {content}")
        
        return requirements if requirements else [content]
    
    def _extract_constraints(self, statement: Statement) -> List[str]:
        """Extract constraints from statement."""
        content = statement.content
        constraints = []
        
        # Look for constraint keywords
        constraint_patterns = [
            'must', 'should', 'cannot', 'limited to', 'restricted',
            'required', 'mandatory', 'forbidden', 'not allowed'
        ]
        
        content_lower = content.lower()
        for pattern in constraint_patterns:
            if pattern in content_lower:
                constraints.append(content)
                break
        
        return constraints if constraints else [content]
    
    def _extract_business_rules(self, statement: Statement) -> List[str]:
        """Extract business rules from statement."""
        content = statement.content
        rules = []
        
        # Look for business rule patterns
        rule_patterns = [
            'if', 'when', 'unless', 'only if', 'provided that',
            'business rule', 'policy', 'regulation', 'compliance'
        ]
        
        content_lower = content.lower()
        for pattern in rule_patterns:
            if pattern in content_lower:
                rules.append(content)
                break
        
        return rules if rules else [content]
    
    def _extract_quality_attributes(self, conversation: Conversation) -> Dict[str, Any]:
        """Extract quality attributes from conversation."""
        attributes = {
            'performance': False,
            'scalability': False,
            'security': False,
            'reliability': False,
            'usability': False
        }
        
        full_text = ' '.join(stmt.content.lower() for stmt in conversation.statements)
        
        for attribute in attributes:
            if attribute in full_text:
                attributes[attribute] = True
        
        return attributes
    
    def _calculate_parsing_confidence(self, conversation: Conversation) -> float:
        """Calculate confidence score for parsing results."""
        total_statements = len(conversation.statements)
        parsed_statements = 0
        
        for statement in conversation.statements:
            # Check if statement has clear structure
            if any(keyword in statement.content.lower() for keyword in [
                'create', 'build', 'implement', 'need', 'want', 'should', 'must'
            ]):
                parsed_statements += 1
        
        return parsed_statements / total_statements if total_statements > 0 else 0.0
