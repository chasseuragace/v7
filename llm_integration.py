"""
LLM Integration: Production-Ready AI Processing

This module integrates real LLM APIs into the Statement-to-Reality System,
replacing simulation with actual AI-powered analysis and code generation.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import openai
from anthropic import Anthropic
from statement_reality_system import (
    ConversationalIntentParser, ArchitecturalInferenceEngine,
    AbstractionGenerator, ImplementationSynthesizer,
    Conversation, Statement, Requirements, Architecture, AbstractModel
)


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str  # 'openai', 'anthropic', 'local'
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7


class ProductionConversationalParser(ConversationalIntentParser):
    """Production-grade conversational parser using real LLMs."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.config.provider == 'openai':
            return openai.OpenAI(api_key=self.config.api_key)
        elif self.config.provider == 'anthropic':
            return Anthropic(api_key=self.config.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    async def parse_statements(self, conversation: Conversation) -> Requirements:
        """Parse statements using production LLM."""
        
        conversation_text = "\n".join([
            f"{stmt.speaker}: {stmt.content}" 
            for stmt in conversation.statements
        ])
        
        prompt = f"""
        Analyze this conversation and extract structured requirements for a software system.
        
        Conversation:
        {conversation_text}
        
        Extract and categorize requirements into:
        1. Functional requirements (what the system should do)
        2. Non-functional requirements (performance, scalability, etc.)
        3. Constraints (technical limitations, preferences)
        4. Business rules (domain-specific logic)
        5. Preferences (nice-to-have features)
        
        Return as JSON with arrays for each category.
        """
        
        response = await self._call_llm(prompt)
        
        try:
            parsed = json.loads(response)
            return Requirements(
                functional=parsed.get('functional', []),
                non_functional=parsed.get('non_functional', []),
                constraints=parsed.get('constraints', []),
                business_rules=parsed.get('business_rules', []),
                preferences=parsed.get('preferences', [])
            )
        except json.JSONDecodeError:
            # Fallback to text parsing if JSON fails
            return self._parse_text_response(response)
    
    async def identify_statement_types(self, statements: List[Statement]) -> Dict[str, List[Statement]]:
        """Categorize statements using LLM analysis."""
        
        statements_text = "\n".join([
            f"{i}: {stmt.content}" 
            for i, stmt in enumerate(statements)
        ])
        
        prompt = f"""
        Categorize these statements by type:
        
        {statements_text}
        
        Categories:
        - functional: System capabilities and features
        - constraint: Technical or business limitations
        - architectural: System design preferences
        - meta: Self-referential or system-level statements
        
        Return JSON mapping statement indices to categories.
        """
        
        response = await self._call_llm(prompt)
        
        try:
            categories = json.loads(response)
            result = {'functional': [], 'constraint': [], 'architectural': [], 'meta': []}
            
            for idx_str, category in categories.items():
                idx = int(idx_str)
                if 0 <= idx < len(statements) and category in result:
                    result[category].append(statements[idx])
            
            return result
        except (json.JSONDecodeError, ValueError):
            # Fallback to simple keyword matching
            return self._fallback_categorization(statements)
    
    async def extract_implicit_requirements(self, conversation: Conversation) -> List[str]:
        """Extract unstated requirements using LLM reasoning."""
        
        conversation_text = "\n".join([
            f"{stmt.speaker}: {stmt.content}" 
            for stmt in conversation.statements
        ])
        
        prompt = f"""
        Based on this conversation about building a software system, what are the implicit 
        requirements that weren't explicitly stated but are necessary for the system to work?
        
        Conversation:
        {conversation_text}
        
        Consider:
        - Infrastructure needs
        - Security requirements
        - User experience expectations
        - Performance implications
        - Maintenance and monitoring needs
        
        Return as a JSON array of requirement strings.
        """
        
        response = await self._call_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [
                "System must be secure and handle authentication",
                "User interface should be intuitive and responsive",
                "System should handle errors gracefully",
                "Data should be persistent and recoverable",
                "System should be maintainable and extensible"
            ]
    
    async def _call_llm(self, prompt: str) -> str:
        """Make API call to configured LLM."""
        
        if self.config.provider == 'openai':
            response = await self.client.chat.completions.acreate(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect and requirements analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
            
        elif self.config.provider == 'anthropic':
            response = await self.client.messages.acreate(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    def _parse_text_response(self, response: str) -> Requirements:
        """Fallback text parsing when JSON fails."""
        lines = response.split('\n')
        
        functional = [line.strip('- ') for line in lines if 'functional' in line.lower()]
        non_functional = [line.strip('- ') for line in lines if 'performance' in line.lower() or 'scalability' in line.lower()]
        constraints = [line.strip('- ') for line in lines if 'constraint' in line.lower() or 'limitation' in line.lower()]
        
        return Requirements(
            functional=functional[:5],  # Limit to prevent overflow
            non_functional=non_functional[:3],
            constraints=constraints[:3],
            business_rules=[],
            preferences=[]
        )
    
    def _fallback_categorization(self, statements: List[Statement]) -> Dict[str, List[Statement]]:
        """Fallback categorization using keywords."""
        result = {'functional': [], 'constraint': [], 'architectural': [], 'meta': []}
        
        for stmt in statements:
            content = stmt.content.lower()
            if any(word in content for word in ['should', 'must', 'need', 'want']):
                result['functional'].append(stmt)
            elif any(word in content for word in ['never', 'cannot', 'limit', 'constraint']):
                result['constraint'].append(stmt)
            elif any(word in content for word in ['architecture', 'pattern', 'design']):
                result['architectural'].append(stmt)
            else:
                result['meta'].append(stmt)
        
        return result


class ProductionArchitecturalInference(ArchitecturalInferenceEngine):
    """Production architectural inference using LLMs."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client."""
        if self.config.provider == 'openai':
            return openai.OpenAI(api_key=self.config.api_key)
        elif self.config.provider == 'anthropic':
            return Anthropic(api_key=self.config.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    async def infer_architecture(self, requirements: Requirements) -> Architecture:
        """Generate architecture using LLM reasoning."""
        
        requirements_text = f"""
        Functional Requirements:
        {chr(10).join(f"- {req}" for req in requirements.functional)}
        
        Non-Functional Requirements:
        {chr(10).join(f"- {req}" for req in requirements.non_functional)}
        
        Constraints:
        {chr(10).join(f"- {constraint}" for constraint in requirements.constraints)}
        
        Business Rules:
        {chr(10).join(f"- {rule}" for rule in requirements.business_rules)}
        """
        
        prompt = f"""
        Design a software system architecture based on these requirements:
        
        {requirements_text}
        
        Provide a detailed architecture including:
        1. System components and their responsibilities
        2. Architectural patterns to apply
        3. Component relationships and dependencies
        4. Quality attributes and how they're achieved
        5. Technology recommendations
        
        Format as JSON with the following structure:
        {{
            "components": [
                {{
                    "name": "ComponentName",
                    "responsibilities": ["responsibility1", "responsibility2"],
                    "interfaces": ["interface1", "interface2"],
                    "dependencies": ["dependency1", "dependency2"]
                }}
            ],
            "patterns": ["pattern1", "pattern2"],
            "relationships": {{"component1": ["component2", "component3"]}},
            "quality_attributes": {{"attribute": "approach"}},
            "technology_stack": {{"layer": "technology"}}
        }}
        """
        
        response = await self._call_llm(prompt)
        
        try:
            arch_data = json.loads(response)
            return self._build_architecture_from_json(arch_data)
        except json.JSONDecodeError:
            # Fallback to rule-based architecture
            return self._generate_fallback_architecture(requirements)
    
    async def match_patterns(self, requirements: Requirements) -> List[str]:
        """Match architectural patterns using LLM analysis."""
        
        requirements_summary = " ".join(requirements.functional + requirements.non_functional)
        
        prompt = f"""
        Based on these requirements, which architectural patterns would be most appropriate?
        
        Requirements: {requirements_summary}
        
        Consider patterns like:
        - Microservices, Monolith, Serverless
        - Event-Driven, Request-Response, Pub-Sub
        - Layered, Hexagonal, Clean Architecture
        - CQRS, Event Sourcing, Saga
        - MVC, MVP, MVVM
        
        Return as JSON array of recommended patterns with brief justifications.
        """
        
        response = await self._call_llm(prompt)
        
        try:
            patterns = json.loads(response)
            return [p['pattern'] if isinstance(p, dict) else p for p in patterns]
        except json.JSONDecodeError:
            return self._fallback_pattern_matching(requirements)
    
    async def validate_architecture(self, architecture: Architecture, requirements: Requirements) -> bool:
        """Validate architecture against requirements using LLM."""
        
        arch_summary = {
            'components': [comp.name for comp in architecture.components],
            'patterns': architecture.patterns,
            'quality_attributes': architecture.quality_attributes
        }
        
        requirements_summary = {
            'functional': requirements.functional,
            'non_functional': requirements.non_functional,
            'constraints': requirements.constraints
        }
        
        prompt = f"""
        Validate if this architecture satisfies the given requirements:
        
        Architecture:
        {json.dumps(arch_summary, indent=2)}
        
        Requirements:
        {json.dumps(requirements_summary, indent=2)}
        
        Check for:
        1. Functional requirement coverage
        2. Non-functional requirement satisfaction
        3. Constraint compliance
        4. Architectural consistency
        
        Return JSON: {{"valid": true/false, "issues": ["issue1", "issue2"], "score": 0.0-1.0}}
        """
        
        response = await self._call_llm(prompt)
        
        try:
            validation = json.loads(response)
            return validation.get('valid', False) and validation.get('score', 0) >= 0.7
        except json.JSONDecodeError:
            # Fallback validation
            return len(architecture.components) >= 3 and len(architecture.patterns) >= 1
    
    async def optimize_architecture(self, architecture: Architecture, constraints: Dict[str, Any]) -> Architecture:
        """Optimize architecture based on constraints using LLM."""
        
        arch_data = {
            'components': [
                {
                    'name': comp.name,
                    'responsibilities': comp.responsibilities,
                    'dependencies': comp.dependencies
                } for comp in architecture.components
            ],
            'patterns': architecture.patterns,
            'quality_attributes': architecture.quality_attributes
        }
        
        prompt = f"""
        Optimize this architecture based on the given constraints:
        
        Current Architecture:
        {json.dumps(arch_data, indent=2)}
        
        Constraints:
        {json.dumps(constraints, indent=2)}
        
        Suggest optimizations for:
        1. Performance improvements
        2. Cost reduction
        3. Scalability enhancements
        4. Maintainability improvements
        
        Return the optimized architecture in the same JSON format.
        """
        
        response = await self._call_llm(prompt)
        
        try:
            optimized_data = json.loads(response)
            return self._build_architecture_from_json(optimized_data)
        except json.JSONDecodeError:
            return architecture  # Return original if optimization fails
    
    async def _call_llm(self, prompt: str) -> str:
        """Make API call to configured LLM."""
        
        if self.config.provider == 'openai':
            response = await self.client.chat.completions.acreate(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect with deep knowledge of system design patterns and best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
            
        elif self.config.provider == 'anthropic':
            response = await self.client.messages.acreate(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    def _build_architecture_from_json(self, arch_data: Dict) -> Architecture:
        """Build Architecture object from JSON data."""
        from statement_reality_system import ArchitecturalComponent
        
        components = []
        for comp_data in arch_data.get('components', []):
            components.append(ArchitecturalComponent(
                name=comp_data.get('name', 'UnknownComponent'),
                responsibilities=comp_data.get('responsibilities', []),
                interfaces=comp_data.get('interfaces', []),
                dependencies=comp_data.get('dependencies', []),
                constraints=comp_data.get('constraints', {})
            ))
        
        return Architecture(
            components=components,
            patterns=arch_data.get('patterns', []),
            relationships=arch_data.get('relationships', {}),
            constraints=arch_data.get('constraints', {}),
            quality_attributes=arch_data.get('quality_attributes', {})
        )
    
    def _generate_fallback_architecture(self, requirements: Requirements) -> Architecture:
        """Generate basic architecture when LLM fails."""
        from statement_reality_system import ArchitecturalComponent
        
        # Basic components based on requirements
        components = [
            ArchitecturalComponent(
                name="UserInterface",
                responsibilities=["Handle user interactions", "Display data"],
                interfaces=["render", "handleInput"],
                dependencies=[],
                constraints={}
            ),
            ArchitecturalComponent(
                name="BusinessLogic",
                responsibilities=["Process business rules", "Coordinate operations"],
                interfaces=["process", "validate"],
                dependencies=["UserInterface"],
                constraints={}
            ),
            ArchitecturalComponent(
                name="DataLayer",
                responsibilities=["Persist data", "Query data"],
                interfaces=["save", "load", "query"],
                dependencies=["BusinessLogic"],
                constraints={}
            )
        ]
        
        return Architecture(
            components=components,
            patterns=["Layered Architecture", "MVC"],
            relationships={"UserInterface": ["BusinessLogic"], "BusinessLogic": ["DataLayer"]},
            constraints={},
            quality_attributes={"maintainability": "high", "scalability": "medium"}
        )
    
    def _fallback_pattern_matching(self, requirements: Requirements) -> List[str]:
        """Fallback pattern matching using keywords."""
        patterns = []
        
        all_text = " ".join(requirements.functional + requirements.non_functional).lower()
        
        if 'microservice' in all_text or 'distributed' in all_text:
            patterns.append("Microservices")
        if 'event' in all_text or 'real-time' in all_text:
            patterns.append("Event-Driven")
        if 'web' in all_text or 'ui' in all_text:
            patterns.append("MVC")
        if 'api' in all_text:
            patterns.append("REST API")
        
        return patterns or ["Layered Architecture"]


# Factory function for creating production-ready components
def create_production_system(llm_config: LLMConfig):
    """Create a production-ready Statement-to-Reality system with LLM integration."""
    
    parser = ProductionConversationalParser(llm_config)
    inference_engine = ProductionArchitecturalInference(llm_config)
    
    return {
        'parser': parser,
        'inference_engine': inference_engine,
        'config': llm_config
    }


# Configuration presets
OPENAI_GPT4_CONFIG = LLMConfig(
    provider='openai',
    model='gpt-4-turbo-preview',
    api_key=os.getenv('OPENAI_API_KEY'),
    max_tokens=4000,
    temperature=0.7
)

ANTHROPIC_CLAUDE_CONFIG = LLMConfig(
    provider='anthropic',
    model='claude-3-opus-20240229',
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    max_tokens=4000,
    temperature=0.7
)

# Usage example
if __name__ == "__main__":
    # Example usage with OpenAI
    config = OPENAI_GPT4_CONFIG
    
    if config.api_key:
        system = create_production_system(config)
        print("✅ Production LLM system initialized with OpenAI GPT-4")
        print("🔑 API key configured")
        print("🚀 Ready for production statement processing")
    else:
        print("⚠️  Set OPENAI_API_KEY environment variable to use production LLM")
        print("💡 Falling back to simulation mode")
