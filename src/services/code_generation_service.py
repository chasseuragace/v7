"""
Refactored code generation service with improved performance and maintainability.
"""

from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio

from src.core.models import SystemArchitecture, GeneratedCode
from src.core.exceptions import CodeGenerationError, UnsupportedLanguageError
from src.core.logging import LoggerMixin, log_processing_time
from src.core.config import get_config
from src.interfaces.base import MultiLanguageGenerator


class CodeGenerationService(LoggerMixin):
    """Enhanced code generation service with parallel processing."""
    
    def __init__(self, generator: MultiLanguageGenerator):
        self.generator = generator
        self.config = get_config()
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_generations)
    
    @log_processing_time
    async def generate_multi_language_code(
        self, 
        architecture: SystemArchitecture,
        languages: List[str]
    ) -> Dict[str, GeneratedCode]:
        """Generate code for multiple languages in parallel."""
        
        self.logger.info(f"Generating code for {len(languages)} languages")
        
        # Create tasks for parallel generation
        tasks = []
        for language in languages:
            if language in self.generator.get_supported_languages():
                task = self._generate_code_async(architecture, language)
                tasks.append((language, task))
            else:
                self.logger.warning(f"Unsupported language: {language}")
        
        # Execute tasks in parallel
        results = {}
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (language, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                self.logger.error(f"Code generation failed for {language}: {result}")
                continue
            results[language] = result
        
        self.logger.info(f"Successfully generated code for {len(results)} languages")
        return results
    
    async def _generate_code_async(self, architecture: SystemArchitecture, language: str) -> GeneratedCode:
        """Generate code asynchronously for a single language."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.generator.generate_code, 
            architecture, 
            language
        )


class EnhancedMultiLanguageGenerator(MultiLanguageGenerator, LoggerMixin):
    """Enhanced multi-language generator with template system."""
    
    def __init__(self):
        self.config = get_config()
        self.supported_languages = self.config.codegen.supported_languages
        self.templates = self._load_templates()
    
    def generate_code(
        self, 
        architecture: SystemArchitecture, 
        language: str, 
        framework: Optional[str] = None
    ) -> GeneratedCode:
        """Generate code for specified language and framework."""
        
        if language not in self.supported_languages:
            raise UnsupportedLanguageError(f"Language {language} not supported")
        
        self.logger.info(f"Generating {language} code")
        
        # Select framework
        if not framework:
            framework = self._get_default_framework(language)
        
        # Generate files
        files = self._generate_files(architecture, language, framework)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(language, framework)
        
        # Determine entry point
        entry_point = self._get_entry_point(language, framework)
        
        return GeneratedCode(
            language=language,
            framework=framework,
            files=files,
            dependencies=dependencies,
            entry_point=entry_point,
            build_commands=self._get_build_commands(language, framework),
            run_commands=self._get_run_commands(language, framework)
        )
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages."""
        return self.supported_languages
    
    def get_supported_frameworks(self, language: str) -> List[str]:
        """Get supported frameworks for language."""
        framework_map = {
            'python': ['fastapi', 'flask', 'django'],
            'rust': ['axum', 'warp', 'actix'],
            'go': ['gin', 'echo', 'fiber'],
            'typescript': ['express', 'nestjs', 'koa'],
            'java': ['spring', 'quarkus'],
            'cpp': ['crow', 'beast']
        }
        return framework_map.get(language, [])
    
    def validate_code(self, code: GeneratedCode) -> List[str]:
        """Validate generated code."""
        issues = []
        
        if not code.files:
            issues.append("No files generated")
        
        if code.entry_point not in code.files:
            issues.append("Entry point file not found")
        
        return issues
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load code templates."""
        return {
            'python': {
                'fastapi': '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{app_name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "Hello from {app_name}"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            },
            'rust': {
                'axum': '''
use axum::{{
    routing::get,
    Router,
    Json,
}};
use serde_json::{{json, Value}};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {{
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health));

    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    println!("Server running on {{}}", addr);
    
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}}

async fn root() -> Json<Value> {{
    Json(json!({{"message": "Hello from {app_name}"}}))
}}

async fn health() -> Json<Value> {{
    Json(json!({{"status": "healthy"}}))
}}
'''
            }
        }
    
    def _generate_files(self, architecture: SystemArchitecture, language: str, framework: str) -> Dict[str, str]:
        """Generate code files."""
        files = {}
        
        # Get template
        template = self.templates.get(language, {}).get(framework, "")
        if template:
            app_name = "generated_app"
            main_content = template.format(app_name=app_name)
            
            # Determine main file name
            main_file = self._get_main_filename(language)
            files[main_file] = main_content
        
        # Generate additional files based on components
        for component in architecture.components:
            component_file = self._generate_component_file(component, language, framework)
            if component_file:
                filename, content = component_file
                files[filename] = content
        
        return files
    
    def _get_default_framework(self, language: str) -> str:
        """Get default framework for language."""
        defaults = {
            'python': 'fastapi',
            'rust': 'axum',
            'go': 'gin',
            'typescript': 'express',
            'java': 'spring',
            'cpp': 'crow'
        }
        return defaults.get(language, 'default')
    
    def _get_main_filename(self, language: str) -> str:
        """Get main filename for language."""
        filenames = {
            'python': 'main.py',
            'rust': 'main.rs',
            'go': 'main.go',
            'typescript': 'index.ts',
            'java': 'Main.java',
            'cpp': 'main.cpp'
        }
        return filenames.get(language, 'main.txt')
    
    def _extract_dependencies(self, language: str, framework: str) -> List[str]:
        """Extract dependencies for language/framework."""
        deps = {
            'python': {
                'fastapi': ['fastapi', 'uvicorn', 'pydantic'],
                'flask': ['flask', 'flask-cors'],
                'django': ['django', 'djangorestframework']
            },
            'rust': {
                'axum': ['axum', 'tokio', 'serde_json'],
                'warp': ['warp', 'tokio', 'serde_json']
            },
            'go': {
                'gin': ['github.com/gin-gonic/gin'],
                'echo': ['github.com/labstack/echo/v4']
            }
        }
        return deps.get(language, {}).get(framework, [])
    
    def _get_entry_point(self, language: str, framework: str) -> str:
        """Get entry point filename."""
        return self._get_main_filename(language)
    
    def _get_build_commands(self, language: str, framework: str) -> List[str]:
        """Get build commands."""
        commands = {
            'python': [],
            'rust': ['cargo build --release'],
            'go': ['go build'],
            'typescript': ['npm run build'],
            'java': ['mvn compile'],
            'cpp': ['make']
        }
        return commands.get(language, [])
    
    def _get_run_commands(self, language: str, framework: str) -> List[str]:
        """Get run commands."""
        commands = {
            'python': ['python main.py'],
            'rust': ['cargo run'],
            'go': ['go run main.go'],
            'typescript': ['npm start'],
            'java': ['java Main'],
            'cpp': ['./main']
        }
        return commands.get(language, [])
    
    def _generate_component_file(self, component, language: str, framework: str) -> Optional[tuple]:
        """Generate file for a component."""
        if language == 'python':
            filename = f"{component.name.lower()}.py"
            content = f'''
"""
{component.name} component
Responsibilities: {', '.join(component.responsibilities)}
"""

class {component.name}:
    def __init__(self):
        pass
    
    def handle_request(self):
        return {{"message": "Handled by {component.name}"}}
'''
            return (filename, content)
        
        return None
