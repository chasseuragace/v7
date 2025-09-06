"""
Refactored architecture inference service.

This service handles architectural inference with improved pattern recognition,
validation, and optimization capabilities.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json

from src.core.models import (
    SystemRequirements, SystemArchitecture, SystemComponent, ProcessingResult
)
from src.core.exceptions import ArchitectureInferenceError, ValidationError
from src.core.logging import LoggerMixin, log_processing_time
from src.core.config import get_config
from src.interfaces.base import ArchitecturalInference


class ArchitectureService(LoggerMixin):
    """Service for architectural inference and validation."""
    
    def __init__(self, inference_engine: ArchitecturalInference):
        self.inference_engine = inference_engine
        self.config = get_config()
        self.pattern_library = self._load_pattern_library()
    
    @log_processing_time
    def infer_and_validate_architecture(self, requirements: SystemRequirements) -> SystemArchitecture:
        """
        Infer architecture from requirements with comprehensive validation.
        
        Args:
            requirements: System requirements
            
        Returns:
            Validated system architecture
        """
        try:
            self.logger.info("Starting architecture inference")
            
            # Infer base architecture
            architecture = self.inference_engine.infer_architecture(requirements)
            
            # Enhance with patterns
            self._apply_architectural_patterns(architecture, requirements)
            
            # Validate architecture
            validation_issues = self.validate_architecture_comprehensive(architecture)
            if validation_issues:
                self.logger.warning(f"Architecture validation issues: {validation_issues}")
                # Try to auto-fix common issues
                self._auto_fix_architecture_issues(architecture, validation_issues)
            
            # Optimize architecture
            self._optimize_architecture(architecture, requirements)
            
            self.logger.info("Architecture inference completed successfully")
            return architecture
            
        except Exception as e:
            self.logger.error(f"Architecture inference failed: {e}")
            raise ArchitectureInferenceError(f"Failed to infer architecture: {str(e)}")
    
    def validate_architecture_comprehensive(self, architecture: SystemArchitecture) -> List[str]:
        """Comprehensive architecture validation."""
        issues = []
        
        # Basic validation
        basic_issues = self.inference_engine.validate_architecture(architecture)
        issues.extend(basic_issues)
        
        # Component validation
        component_issues = self._validate_components(architecture.components)
        issues.extend(component_issues)
        
        # Relationship validation
        relationship_issues = self._validate_relationships(architecture)
        issues.extend(relationship_issues)
        
        # Pattern validation
        pattern_issues = self._validate_patterns(architecture)
        issues.extend(pattern_issues)
        
        # Technology stack validation
        tech_issues = self._validate_technology_stack(architecture)
        issues.extend(tech_issues)
        
        return issues
    
    def _validate_components(self, components: List[SystemComponent]) -> List[str]:
        """Validate individual components."""
        issues = []
        
        if not components:
            issues.append("Architecture has no components")
            return issues
        
        component_names = set()
        for component in components:
            # Check for duplicate names
            if component.name in component_names:
                issues.append(f"Duplicate component name: {component.name}")
            component_names.add(component.name)
            
            # Validate component structure
            if not component.responsibilities:
                issues.append(f"Component {component.name} has no responsibilities")
            
            if not component.component_type:
                issues.append(f"Component {component.name} has no type")
        
        return issues
    
    def _validate_relationships(self, architecture: SystemArchitecture) -> List[str]:
        """Validate component relationships."""
        issues = []
        
        component_names = {c.name for c in architecture.components}
        
        for relationship in architecture.relationships:
            source = relationship.get('source')
            target = relationship.get('target')
            
            if not source or not target:
                issues.append("Relationship missing source or target")
                continue
            
            if source not in component_names:
                issues.append(f"Relationship references unknown component: {source}")
            
            if target not in component_names:
                issues.append(f"Relationship references unknown component: {target}")
        
        return issues
    
    def _validate_patterns(self, architecture: SystemArchitecture) -> List[str]:
        """Validate architectural patterns."""
        issues = []
        
        for pattern in architecture.patterns:
            if pattern not in self.pattern_library:
                issues.append(f"Unknown architectural pattern: {pattern}")
            else:
                # Validate pattern requirements
                pattern_requirements = self.pattern_library[pattern].get('requirements', [])
                for requirement in pattern_requirements:
                    if not self._check_pattern_requirement(architecture, requirement):
                        issues.append(f"Pattern {pattern} requirement not met: {requirement}")
        
        return issues
    
    def _validate_technology_stack(self, architecture: SystemArchitecture) -> List[str]:
        """Validate technology stack compatibility."""
        issues = []
        
        tech_stack = architecture.technology_stack
        
        # Check for conflicting technologies
        conflicts = self._check_technology_conflicts(tech_stack)
        issues.extend(conflicts)
        
        # Check for missing dependencies
        missing_deps = self._check_missing_dependencies(tech_stack)
        issues.extend(missing_deps)
        
        return issues
    
    def _apply_architectural_patterns(self, architecture: SystemArchitecture, requirements: SystemRequirements) -> None:
        """Apply appropriate architectural patterns."""
        suggested_patterns = self.inference_engine.suggest_patterns(requirements)
        
        for pattern in suggested_patterns:
            if pattern in self.pattern_library:
                self._apply_pattern(architecture, pattern)
    
    def _apply_pattern(self, architecture: SystemArchitecture, pattern: str) -> None:
        """Apply a specific architectural pattern."""
        pattern_config = self.pattern_library.get(pattern, {})
        
        # Add pattern-specific components
        pattern_components = pattern_config.get('components', [])
        for comp_config in pattern_components:
            if not any(c.name == comp_config['name'] for c in architecture.components):
                component = SystemComponent(
                    name=comp_config['name'],
                    component_type=comp_config['type'],
                    responsibilities=comp_config.get('responsibilities', []),
                    interfaces=comp_config.get('interfaces', []),
                    dependencies=comp_config.get('dependencies', [])
                )
                architecture.components.append(component)
        
        # Add pattern-specific relationships
        pattern_relationships = pattern_config.get('relationships', [])
        architecture.relationships.extend(pattern_relationships)
        
        # Add pattern to architecture
        if pattern not in architecture.patterns:
            architecture.patterns.append(pattern)
    
    def _optimize_architecture(self, architecture: SystemArchitecture, requirements: SystemRequirements) -> None:
        """Optimize architecture based on requirements."""
        # Optimize for performance if required
        if requirements.quality_attributes.get('performance'):
            self._optimize_for_performance(architecture)
        
        # Optimize for scalability if required
        if requirements.quality_attributes.get('scalability'):
            self._optimize_for_scalability(architecture)
        
        # Optimize for security if required
        if requirements.quality_attributes.get('security'):
            self._optimize_for_security(architecture)
    
    def _optimize_for_performance(self, architecture: SystemArchitecture) -> None:
        """Apply performance optimizations."""
        # Add caching components
        if not any(c.component_type == 'cache' for c in architecture.components):
            cache_component = SystemComponent(
                name="CacheLayer",
                component_type="cache",
                responsibilities=["Data caching", "Performance optimization"],
                interfaces=["CacheInterface"],
                dependencies=[]
            )
            architecture.components.append(cache_component)
        
        # Add load balancer if multiple services
        service_components = [c for c in architecture.components if c.component_type == 'service']
        if len(service_components) > 1:
            if not any(c.component_type == 'load_balancer' for c in architecture.components):
                lb_component = SystemComponent(
                    name="LoadBalancer",
                    component_type="load_balancer",
                    responsibilities=["Load distribution", "High availability"],
                    interfaces=["LoadBalancerInterface"],
                    dependencies=[]
                )
                architecture.components.append(lb_component)
    
    def _optimize_for_scalability(self, architecture: SystemArchitecture) -> None:
        """Apply scalability optimizations."""
        # Ensure microservices pattern for scalability
        if 'microservices' not in architecture.patterns:
            architecture.patterns.append('microservices')
        
        # Add message queue for async processing
        if not any(c.component_type == 'message_queue' for c in architecture.components):
            queue_component = SystemComponent(
                name="MessageQueue",
                component_type="message_queue",
                responsibilities=["Async message processing", "Service decoupling"],
                interfaces=["MessageQueueInterface"],
                dependencies=[]
            )
            architecture.components.append(queue_component)
    
    def _optimize_for_security(self, architecture: SystemArchitecture) -> None:
        """Apply security optimizations."""
        # Add authentication service
        if not any('auth' in c.name.lower() for c in architecture.components):
            auth_component = SystemComponent(
                name="AuthenticationService",
                component_type="service",
                responsibilities=["User authentication", "Token management"],
                interfaces=["AuthInterface"],
                dependencies=[]
            )
            architecture.components.append(auth_component)
        
        # Add API gateway for security
        if not any(c.component_type == 'api_gateway' for c in architecture.components):
            gateway_component = SystemComponent(
                name="APIGateway",
                component_type="api_gateway",
                responsibilities=["Request routing", "Authentication", "Rate limiting"],
                interfaces=["GatewayInterface"],
                dependencies=[]
            )
            architecture.components.append(gateway_component)
    
    def _auto_fix_architecture_issues(self, architecture: SystemArchitecture, issues: List[str]) -> None:
        """Attempt to automatically fix common architecture issues."""
        for issue in issues:
            if "has no responsibilities" in issue:
                component_name = issue.split()[1]
                component = architecture.get_component_by_name(component_name)
                if component:
                    component.responsibilities = [f"Handle {component.component_type} operations"]
            
            elif "has no type" in issue:
                component_name = issue.split()[1]
                component = architecture.get_component_by_name(component_name)
                if component:
                    component.component_type = "service"  # Default type
    
    def _load_pattern_library(self) -> Dict[str, Any]:
        """Load architectural pattern library."""
        return {
            'layered': {
                'description': 'Layered architecture pattern',
                'components': [
                    {'name': 'PresentationLayer', 'type': 'layer', 'responsibilities': ['UI handling']},
                    {'name': 'BusinessLayer', 'type': 'layer', 'responsibilities': ['Business logic']},
                    {'name': 'DataLayer', 'type': 'layer', 'responsibilities': ['Data access']}
                ],
                'relationships': [
                    {'source': 'PresentationLayer', 'target': 'BusinessLayer', 'type': 'depends_on'},
                    {'source': 'BusinessLayer', 'target': 'DataLayer', 'type': 'depends_on'}
                ],
                'requirements': ['clear_separation_of_concerns']
            },
            'microservices': {
                'description': 'Microservices architecture pattern',
                'components': [
                    {'name': 'APIGateway', 'type': 'api_gateway', 'responsibilities': ['Request routing']},
                    {'name': 'ServiceRegistry', 'type': 'registry', 'responsibilities': ['Service discovery']}
                ],
                'relationships': [],
                'requirements': ['service_independence', 'distributed_deployment']
            },
            'mvc': {
                'description': 'Model-View-Controller pattern',
                'components': [
                    {'name': 'Model', 'type': 'model', 'responsibilities': ['Data management']},
                    {'name': 'View', 'type': 'view', 'responsibilities': ['UI presentation']},
                    {'name': 'Controller', 'type': 'controller', 'responsibilities': ['Request handling']}
                ],
                'relationships': [
                    {'source': 'Controller', 'target': 'Model', 'type': 'uses'},
                    {'source': 'Controller', 'target': 'View', 'type': 'updates'},
                    {'source': 'View', 'target': 'Model', 'type': 'observes'}
                ],
                'requirements': ['clear_mvc_separation']
            },
            'event_driven': {
                'description': 'Event-driven architecture pattern',
                'components': [
                    {'name': 'EventBus', 'type': 'event_bus', 'responsibilities': ['Event routing']},
                    {'name': 'EventStore', 'type': 'storage', 'responsibilities': ['Event persistence']}
                ],
                'relationships': [],
                'requirements': ['event_based_communication']
            }
        }
    
    def _check_pattern_requirement(self, architecture: SystemArchitecture, requirement: str) -> bool:
        """Check if architecture meets pattern requirement."""
        # Simple requirement checking (can be enhanced)
        if requirement == 'clear_separation_of_concerns':
            return len(architecture.components) >= 3
        elif requirement == 'service_independence':
            return len([c for c in architecture.components if c.component_type == 'service']) >= 2
        elif requirement == 'distributed_deployment':
            return 'microservices' in architecture.deployment_model.lower()
        elif requirement == 'clear_mvc_separation':
            mvc_types = {'model', 'view', 'controller'}
            component_types = {c.component_type for c in architecture.components}
            return mvc_types.issubset(component_types)
        elif requirement == 'event_based_communication':
            return any('event' in c.component_type for c in architecture.components)
        
        return True  # Default to true for unknown requirements
    
    def _check_technology_conflicts(self, tech_stack: Dict[str, List[str]]) -> List[str]:
        """Check for conflicting technologies."""
        conflicts = []
        
        # Define known conflicts
        conflict_rules = {
            ('mysql', 'postgresql'): "Cannot use both MySQL and PostgreSQL",
            ('react', 'vue'): "Cannot use both React and Vue in frontend",
            ('express', 'fastify'): "Cannot use both Express and Fastify"
        }
        
        all_technologies = []
        for category, techs in tech_stack.items():
            all_technologies.extend([t.lower() for t in techs])
        
        for (tech1, tech2), message in conflict_rules.items():
            if tech1 in all_technologies and tech2 in all_technologies:
                conflicts.append(message)
        
        return conflicts
    
    def _check_missing_dependencies(self, tech_stack: Dict[str, List[str]]) -> List[str]:
        """Check for missing technology dependencies."""
        missing = []
        
        # Define dependency rules
        dependency_rules = {
            'react': ['nodejs'],
            'vue': ['nodejs'],
            'django': ['python'],
            'flask': ['python'],
            'spring': ['java'],
            'express': ['nodejs']
        }
        
        all_technologies = []
        for category, techs in tech_stack.items():
            all_technologies.extend([t.lower() for t in techs])
        
        for tech, deps in dependency_rules.items():
            if tech in all_technologies:
                for dep in deps:
                    if dep not in all_technologies:
                        missing.append(f"Technology {tech} requires {dep}")
        
        return missing


class EnhancedArchitecturalInference(ArchitecturalInference, LoggerMixin):
    """Enhanced architectural inference with improved pattern recognition."""
    
    def __init__(self):
        self.config = get_config()
        self.component_templates = self._load_component_templates()
    
    def infer_architecture(self, requirements: SystemRequirements) -> SystemArchitecture:
        """Infer system architecture from requirements."""
        self.logger.info("Inferring architecture from requirements")
        
        # Analyze requirements to determine architecture type
        arch_type = self._determine_architecture_type(requirements)
        
        # Generate components based on requirements
        components = self._generate_components(requirements)
        
        # Generate relationships
        relationships = self._generate_relationships(components, requirements)
        
        # Suggest patterns
        patterns = self.suggest_patterns(requirements)
        
        # Determine technology stack
        tech_stack = self._determine_technology_stack(requirements)
        
        # Determine deployment model
        deployment_model = self._determine_deployment_model(requirements)
        
        return SystemArchitecture(
            components=components,
            relationships=relationships,
            patterns=patterns,
            quality_attributes=requirements.quality_attributes,
            technology_stack=tech_stack,
            deployment_model=deployment_model,
            metadata={
                'architecture_type': arch_type,
                'inference_timestamp': datetime.now().isoformat(),
                'requirements_confidence': requirements.confidence_score
            }
        )
    
    def suggest_patterns(self, requirements: SystemRequirements) -> List[str]:
        """Suggest architectural patterns based on requirements."""
        patterns = []
        
        # Analyze functional requirements
        func_reqs_text = ' '.join(requirements.functional_requirements).lower()
        
        # Suggest patterns based on keywords
        if any(word in func_reqs_text for word in ['api', 'service', 'microservice']):
            patterns.append('microservices')
        
        if any(word in func_reqs_text for word in ['web', 'ui', 'interface']):
            patterns.append('mvc')
        
        if any(word in func_reqs_text for word in ['event', 'notification', 'async']):
            patterns.append('event_driven')
        
        if any(word in func_reqs_text for word in ['layer', 'tier']):
            patterns.append('layered')
        
        # Suggest patterns based on quality attributes
        if requirements.quality_attributes.get('scalability'):
            patterns.append('microservices')
        
        if requirements.quality_attributes.get('performance'):
            patterns.append('caching')
        
        # Default pattern if none suggested
        if not patterns:
            patterns.append('layered')
        
        return list(set(patterns))  # Remove duplicates
    
    def validate_architecture(self, architecture: SystemArchitecture) -> List[str]:
        """Validate architecture and return issues."""
        issues = []
        
        # Check basic structure
        if not architecture.components:
            issues.append("Architecture has no components")
        
        if not architecture.patterns:
            issues.append("Architecture has no patterns defined")
        
        # Check component completeness
        for component in architecture.components:
            if not component.responsibilities:
                issues.append(f"Component {component.name} has no responsibilities")
        
        return issues
    
    def _determine_architecture_type(self, requirements: SystemRequirements) -> str:
        """Determine the overall architecture type."""
        func_reqs_text = ' '.join(requirements.functional_requirements).lower()
        
        if 'microservice' in func_reqs_text:
            return 'microservices'
        elif any(word in func_reqs_text for word in ['web', 'api', 'rest']):
            return 'web_application'
        elif 'mobile' in func_reqs_text:
            return 'mobile_application'
        elif any(word in func_reqs_text for word in ['desktop', 'gui']):
            return 'desktop_application'
        else:
            return 'web_application'  # Default
    
    def _generate_components(self, requirements: SystemRequirements) -> List[SystemComponent]:
        """Generate system components from requirements."""
        components = []
        
        # Analyze entities to create components
        for entity in requirements.extracted_entities:
            if entity in self.component_templates:
                template = self.component_templates[entity]
                component = SystemComponent(
                    name=template['name'],
                    component_type=template['type'],
                    responsibilities=template['responsibilities'],
                    interfaces=template['interfaces'],
                    dependencies=template.get('dependencies', [])
                )
                components.append(component)
        
        # Add default components if none generated
        if not components:
            components.extend(self._get_default_components())
        
        return components
    
    def _generate_relationships(self, components: List[SystemComponent], requirements: SystemRequirements) -> List[Dict[str, Any]]:
        """Generate relationships between components."""
        relationships = []
        
        # Create basic relationships based on component types
        api_components = [c for c in components if 'api' in c.component_type.lower()]
        db_components = [c for c in components if 'database' in c.component_type.lower()]
        service_components = [c for c in components if c.component_type == 'service']
        
        # API to service relationships
        for api_comp in api_components:
            for service_comp in service_components:
                relationships.append({
                    'source': api_comp.name,
                    'target': service_comp.name,
                    'type': 'calls',
                    'description': f"{api_comp.name} calls {service_comp.name}"
                })
        
        # Service to database relationships
        for service_comp in service_components:
            for db_comp in db_components:
                relationships.append({
                    'source': service_comp.name,
                    'target': db_comp.name,
                    'type': 'uses',
                    'description': f"{service_comp.name} uses {db_comp.name}"
                })
        
        return relationships
    
    def _determine_technology_stack(self, requirements: SystemRequirements) -> Dict[str, List[str]]:
        """Determine appropriate technology stack."""
        tech_stack = {
            'backend': [],
            'frontend': [],
            'database': [],
            'infrastructure': []
        }
        
        # Analyze requirements for technology hints
        all_text = ' '.join(
            requirements.functional_requirements + 
            requirements.non_functional_requirements
        ).lower()
        
        # Backend technologies
        if 'python' in all_text or 'django' in all_text or 'flask' in all_text:
            tech_stack['backend'].append('Python')
            tech_stack['backend'].append('FastAPI')
        elif 'node' in all_text or 'javascript' in all_text:
            tech_stack['backend'].append('Node.js')
            tech_stack['backend'].append('Express')
        elif 'java' in all_text or 'spring' in all_text:
            tech_stack['backend'].append('Java')
            tech_stack['backend'].append('Spring Boot')
        else:
            # Default stack
            tech_stack['backend'].extend(['Python', 'FastAPI'])
        
        # Frontend technologies
        if 'react' in all_text:
            tech_stack['frontend'].append('React')
        elif 'vue' in all_text:
            tech_stack['frontend'].append('Vue.js')
        elif 'angular' in all_text:
            tech_stack['frontend'].append('Angular')
        else:
            tech_stack['frontend'].append('React')  # Default
        
        # Database technologies
        if 'postgresql' in all_text or 'postgres' in all_text:
            tech_stack['database'].append('PostgreSQL')
        elif 'mysql' in all_text:
            tech_stack['database'].append('MySQL')
        elif 'mongodb' in all_text or 'mongo' in all_text:
            tech_stack['database'].append('MongoDB')
        else:
            tech_stack['database'].append('PostgreSQL')  # Default
        
        # Infrastructure
        tech_stack['infrastructure'].extend(['Docker', 'Kubernetes'])
        
        return tech_stack
    
    def _determine_deployment_model(self, requirements: SystemRequirements) -> str:
        """Determine deployment model."""
        all_text = ' '.join(
            requirements.functional_requirements + 
            requirements.non_functional_requirements
        ).lower()
        
        if 'cloud' in all_text or 'aws' in all_text or 'gcp' in all_text:
            return 'cloud'
        elif 'container' in all_text or 'docker' in all_text:
            return 'containerized'
        elif 'serverless' in all_text:
            return 'serverless'
        else:
            return 'cloud'  # Default
    
    def _load_component_templates(self) -> Dict[str, Any]:
        """Load component templates for common entities."""
        return {
            'api': {
                'name': 'APIService',
                'type': 'api',
                'responsibilities': ['Handle HTTP requests', 'Route requests'],
                'interfaces': ['RestAPI', 'HTTPInterface']
            },
            'database': {
                'name': 'DatabaseService',
                'type': 'database',
                'responsibilities': ['Data storage', 'Data retrieval'],
                'interfaces': ['DatabaseInterface']
            },
            'user': {
                'name': 'UserService',
                'type': 'service',
                'responsibilities': ['User management', 'Authentication'],
                'interfaces': ['UserInterface']
            },
            'authentication': {
                'name': 'AuthenticationService',
                'type': 'service',
                'responsibilities': ['User authentication', 'Token management'],
                'interfaces': ['AuthInterface']
            },
            'payment': {
                'name': 'PaymentService',
                'type': 'service',
                'responsibilities': ['Payment processing', 'Transaction management'],
                'interfaces': ['PaymentInterface']
            },
            'notification': {
                'name': 'NotificationService',
                'type': 'service',
                'responsibilities': ['Send notifications', 'Message delivery'],
                'interfaces': ['NotificationInterface']
            }
        }
    
    def _get_default_components(self) -> List[SystemComponent]:
        """Get default components for basic architecture."""
        return [
            SystemComponent(
                name="APIGateway",
                component_type="api_gateway",
                responsibilities=["Request routing", "Authentication"],
                interfaces=["HTTPInterface"],
                dependencies=[]
            ),
            SystemComponent(
                name="BusinessService",
                component_type="service",
                responsibilities=["Business logic", "Data processing"],
                interfaces=["BusinessInterface"],
                dependencies=["DatabaseService"]
            ),
            SystemComponent(
                name="DatabaseService",
                component_type="database",
                responsibilities=["Data persistence", "Data retrieval"],
                interfaces=["DatabaseInterface"],
                dependencies=[]
            )
        ]
