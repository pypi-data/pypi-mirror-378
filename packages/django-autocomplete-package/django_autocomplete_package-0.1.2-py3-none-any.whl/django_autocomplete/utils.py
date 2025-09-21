import os
import ast
import json
from pathlib import Path
from django.conf import settings

def get_project_root():
    """Get the Django project root directory"""
    return Path(settings.BASE_DIR)

def get_apps_list():
    """Get list of all installed apps in the Django project"""
    return settings.INSTALLED_APPS

def find_python_files(directory):
    """Find all Python files in a directory"""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_classes_from_file(file_path):
    """Extract class definitions from a Python file"""
    classes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno
                    })
        except SyntaxError:
            pass  # Skip files with syntax errors
    return classes

def build_class_index(project_root, apps):
    """Build an index of all classes in the project"""
    class_index = {}
    
    # Add project-level files
    project_files = find_python_files(project_root)
    for file_path in project_files:
        classes = extract_classes_from_file(file_path)
        for cls in classes:
            class_index[cls['name']] = cls
    
    # Add app-level files
    for app in apps:
        if '.' in app:  # Skip dotted app names
            continue
            
        app_path = os.path.join(project_root, app.replace('.', os.sep))
        if os.path.exists(app_path):
            app_files = find_python_files(app_path)
            for file_path in app_files:
                classes = extract_classes_from_file(file_path)
                for cls in classes:
                    class_index[cls['name']] = cls
    
    return class_index

def save_class_index(class_index, file_path):
    """Save the class index to a JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(class_index, f, indent=2)

def load_class_index(file_path):
    """Load the class index from a JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_import_statement(class_name, class_info, current_file):
    """Generate the import statement for a class"""
    file_path = class_info['file']
    relative_path = os.path.relpath(file_path, os.path.dirname(current_file))
    
    # Convert file path to module path
    if relative_path.startswith('..'):
        # Outside current directory
        module_path = file_path.replace(os.path.sep, '.')
        if module_path.endswith('.py'):
            module_path = module_path[:-3]
        if module_path.startswith('.'):
            module_path = module_path[1:]
    else:
        # Inside current directory or subdirectory
        module_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        if module_path.startswith('.'):
            module_path = module_path[1:]
    
    return f"from {module_path} import {class_name}"

def get_existing_imports(file_content):
    """Extract existing imports from file content"""
    imports = []
    lines = file_content.split('\n')
    for line in lines:
        if line.startswith('from ') or line.startswith('import '):
            imports.append(line.strip())
    return imports