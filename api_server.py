"""
API Server: Bridge between Web UI and Statement-Reality System

This server exposes the Python backend as REST APIs for the web interface.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from conversation_processor import ConcreteStatementToRealitySystem, Statement, Conversation
from statement_reality_system import Requirements

app = Flask(__name__)
CORS(app)

# Initialize the statement-to-reality system
reality_system = ConcreteStatementToRealitySystem()

@app.route('/')
def serve_ui():
    """Serve the main UI."""
    return send_from_directory('ui', 'index.html')

@app.route('/ui/<path:filename>')
def serve_ui_files(filename):
    """Serve UI static files."""
    return send_from_directory('ui', filename)

@app.route('/api/process-statement', methods=['POST'])
def process_statement():
    """Process a natural language statement and return the generated reality."""
    try:
        data = request.json
        statement_text = data.get('statement', '')
        
        if not statement_text.strip():
            return jsonify({'error': 'Statement cannot be empty'}), 400
        
        # Create conversation from statement
        statement = Statement(
            content=statement_text,
            context=data.get('context', {}),
            timestamp=data.get('timestamp', '2024-01-01T00:00:00'),
            speaker='user',
            statement_type='functional'
        )
        
        conversation = Conversation(
            statements=[statement],
            metadata={'source': 'web_ui', 'environment': data.get('environment', {})},
            conversation_id=f"web_session_{hash(statement_text)}"
        )
        
        # Process through the system
        requirements = reality_system.parser.parse_statements(conversation)
        architecture = reality_system.inference_engine.infer_architecture(requirements)
        running_system = reality_system.manifest_from_conversation(conversation)
        
        # Generate actual code based on the statement
        generated_code = generate_code_from_statement(statement_text, data.get('environment', {}))
        
        return jsonify({
            'success': True,
            'analysis': {
                'requirements_count': len(requirements.functional + requirements.non_functional),
                'architecture_components': len(architecture.components),
                'patterns': architecture.patterns,
                'quality_attributes': architecture.quality_attributes
            },
            'architecture': {
                'components': [comp.name for comp in architecture.components],
                'relationships': architecture.relationships,
                'constraints': architecture.constraints
            },
            'generated_code': generated_code,
            'system_status': running_system.status,
            'endpoints': running_system.endpoints
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-environment', methods=['POST'])
def analyze_environment():
    """Analyze the provided environment data."""
    try:
        env_data = request.json
        
        analysis = {
            'platform_optimization': determine_platform_optimizations(env_data),
            'resource_constraints': analyze_resource_constraints(env_data),
            'capability_detection': detect_capabilities(env_data),
            'recommendations': generate_recommendations(env_data)
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evolve-system', methods=['POST'])
def evolve_system():
    """Evolve an existing system with new statements."""
    try:
        data = request.json
        new_statements = [
            Statement(
                content=stmt['content'],
                context=stmt.get('context', {}),
                timestamp=stmt.get('timestamp', '2024-01-01T00:00:00'),
                speaker=stmt.get('speaker', 'user'),
                statement_type=stmt.get('type', 'enhancement')
            ) for stmt in data.get('statements', [])
        ]
        
        # Simulate system evolution
        evolved_system = reality_system.evolve_system(
            data.get('current_system', {}), 
            new_statements
        )
        
        return jsonify({
            'success': True,
            'evolved_system': {
                'status': evolved_system.status,
                'new_capabilities': ['Enhanced based on new statements'],
                'updated_endpoints': evolved_system.endpoints
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_code_from_statement(statement, environment):
    """Generate actual code based on the statement and environment."""
    statement_lower = statement.lower()
    
    if 'todo' in statement_lower or 'task' in statement_lower:
        return generate_todo_app(environment)
    elif 'chat' in statement_lower or 'messaging' in statement_lower:
        return generate_chat_app(environment)
    elif 'dashboard' in statement_lower or 'analytics' in statement_lower:
        return generate_dashboard_app(environment)
    else:
        return generate_generic_app(statement, environment)

def generate_todo_app(environment):
    """Generate a todo application optimized for the environment."""
    return {
        'type': 'web_application',
        'framework': 'vanilla_js',
        'files': {
            'index.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Generated Todo App</title>
    <style>
        body { font-family: system-ui; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; }
        .todo-input { width: 100%; padding: 12px; margin-bottom: 20px; border: 2px solid #007acc; border-radius: 8px; }
        .todo-item { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .completed { opacity: 0.6; text-decoration: line-through; }
        button { background: #007acc; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Statement-Generated Todo App</h1>
        <input type="text" class="todo-input" id="todoInput" placeholder="Add a new todo...">
        <button onclick="addTodo()">Add Todo</button>
        <div id="todoList"></div>
    </div>
    <script>
        let todos = JSON.parse(localStorage.getItem('todos') || '[]');
        
        function renderTodos() {
            const list = document.getElementById('todoList');
            list.innerHTML = todos.map((todo, i) => `
                <div class="todo-item ${todo.completed ? 'completed' : ''}">
                    <input type="checkbox" ${todo.completed ? 'checked' : ''} onchange="toggleTodo(${i})">
                    ${todo.text}
                    <button onclick="deleteTodo(${i})" style="float: right; background: #dc3545;">Delete</button>
                </div>
            `).join('');
        }
        
        function addTodo() {
            const input = document.getElementById('todoInput');
            if (input.value.trim()) {
                todos.push({ text: input.value, completed: false });
                input.value = '';
                saveTodos();
                renderTodos();
            }
        }
        
        function toggleTodo(index) {
            todos[index].completed = !todos[index].completed;
            saveTodos();
            renderTodos();
        }
        
        function deleteTodo(index) {
            todos.splice(index, 1);
            saveTodos();
            renderTodos();
        }
        
        function saveTodos() {
            localStorage.setItem('todos', JSON.stringify(todos));
        }
        
        renderTodos();
        document.getElementById('todoInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addTodo();
        });
    </script>
</body>
</html>''',
            'README.md': f'''# Generated Todo Application

This application was automatically generated from the statement and optimized for:
- Platform: {environment.get('platform', 'Unknown')}
- Screen: {environment.get('screen', 'Unknown')}
- Storage: localStorage (detected: {environment.get('localStorage', False)})

## Features
- Add/delete todos
- Mark as complete
- Persistent storage
- Responsive design

Generated by Statement-to-Reality System
'''
        },
        'deployment': {
            'type': 'static_web',
            'requirements': ['Modern web browser', 'localStorage support'],
            'optimizations': [
                f"Optimized for {environment.get('platform', 'web')}",
                f"Responsive design for {environment.get('screen', 'any screen size')}",
                "No external dependencies for maximum compatibility"
            ]
        }
    }

def generate_chat_app(environment):
    """Generate a chat application."""
    return {
        'type': 'web_application',
        'framework': 'vanilla_js_websocket',
        'files': {
            'index.html': '<!-- Chat app HTML would be generated here -->',
            'app.js': '// Chat functionality',
            'style.css': '/* Chat styling */'
        },
        'deployment': {
            'type': 'web_with_backend',
            'requirements': ['WebSocket support', 'Real-time capabilities']
        }
    }

def generate_dashboard_app(environment):
    """Generate a dashboard application."""
    return {
        'type': 'web_application',
        'framework': 'vanilla_js_charts',
        'files': {
            'index.html': '<!-- Dashboard HTML -->',
            'dashboard.js': '// Dashboard logic',
            'charts.js': '// Chart generation'
        }
    }

def generate_generic_app(statement, environment):
    """Generate a generic application based on the statement."""
    return {
        'type': 'web_application',
        'framework': 'vanilla_js',
        'files': {
            'index.html': f'''<!DOCTYPE html>
<html>
<head>
    <title>Generated Application</title>
    <style>
        body {{ font-family: system-ui; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Generated from Statement</h1>
        <p>Statement: "{statement}"</p>
        <p>Environment: {environment.get('platform', 'Unknown')}</p>
        <div id="app">
            <!-- Application content would be generated based on statement analysis -->
        </div>
    </div>
</body>
</html>''',
            'README.md': f'# Generated Application\n\nCreated from: "{statement}"\n\nOptimized for detected environment.'
        }
    }

def determine_platform_optimizations(env_data):
    """Determine optimizations based on platform."""
    platform = env_data.get('platform', '')
    optimizations = []
    
    if 'mac' in platform.lower():
        optimizations.extend(['Safari optimization', 'macOS native feel', 'Retina display support'])
    elif 'win' in platform.lower():
        optimizations.extend(['Edge compatibility', 'Windows UI patterns', 'High DPI support'])
    elif 'linux' in platform.lower():
        optimizations.extend(['Firefox optimization', 'GTK themes', 'Accessibility features'])
    
    return optimizations

def analyze_resource_constraints(env_data):
    """Analyze resource constraints."""
    return {
        'memory': f"{env_data.get('memory', 'Unknown')} GB available",
        'cores': f"{env_data.get('cores', 'Unknown')} CPU cores",
        'storage': 'localStorage available' if env_data.get('localStorage') else 'Limited storage',
        'network': 'Online capabilities detected' if env_data.get('serviceWorker') else 'Offline-first recommended'
    }

def detect_capabilities(env_data):
    """Detect browser/environment capabilities."""
    capabilities = []
    
    if env_data.get('webGL'):
        capabilities.append('WebGL graphics support')
    if env_data.get('serviceWorker'):
        capabilities.append('Service Worker (PWA capable)')
    if env_data.get('pushNotifications'):
        capabilities.append('Push notifications')
    if env_data.get('geolocation'):
        capabilities.append('Geolocation services')
    if env_data.get('localStorage'):
        capabilities.append('Local storage persistence')
    
    return capabilities

def generate_recommendations(env_data):
    """Generate recommendations based on environment."""
    recommendations = []
    
    screen_width = int(env_data.get('screen', '1920x1080').split('x')[0])
    if screen_width < 768:
        recommendations.append('Mobile-first responsive design')
    elif screen_width > 1920:
        recommendations.append('High-resolution display optimization')
    
    if env_data.get('memory', 0) < 4:
        recommendations.append('Lightweight implementation recommended')
    
    if not env_data.get('serviceWorker'):
        recommendations.append('Consider offline-first architecture')
    
    return recommendations

if __name__ == '__main__':
    print("🚀 Starting Statement-to-Reality API Server...")
    print("🌐 Web UI available at: http://localhost:5000")
    print("📡 API endpoints:")
    print("   POST /api/process-statement - Process natural language statements")
    print("   POST /api/analyze-environment - Analyze environment constraints")
    print("   POST /api/evolve-system - Evolve existing systems")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
