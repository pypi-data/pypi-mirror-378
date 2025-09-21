import os
import sys
import json
from pathlib import Path

# Windows-compatible readline import
try:
    import readline  # For Unix-like systems
except ImportError:
    try:
        import pyreadline3 as readline  # For Windows
    except ImportError:
        print("Warning: readline functionality not available")
        readline = None

from django.core.management import execute_from_command_line
from .utils import (
    get_project_root, get_apps_list, build_class_index, 
    save_class_index, load_class_index, get_import_statement,
    get_existing_imports
)

def setup_django():
    """Setup Django environment"""
    # Try to get the settings module from environment or use a default
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
    
    # Add the project root to Python path
    try:
        from django.conf import settings
        project_root = get_project_root()
        sys.path.append(str(project_root))
    except ImportError:
        print("Django not configured properly. Make sure you're in a Django project directory.")
        sys.exit(1)

def generate_class_index():
    """Generate index of all classes in the project"""
    setup_django()
    try:
        project_root = get_project_root()
        apps = get_apps_list()
        
        class_index = build_class_index(project_root, apps)
        index_file = project_root / '.class_index.json'
        save_class_index(class_index, index_file)
        
        print(f"Generated index with {len(class_index)} classes")
        return class_index
    except Exception as e:
        print(f"Error generating index: {e}")
        return {}

def get_suggestions(class_index, partial_name):
    """Get class suggestions based on partial name"""
    suggestions = []
    for class_name in class_index.keys():
        if partial_name.lower() in class_name.lower():
            suggestions.append(class_name)
    return sorted(suggestions)[:10]  # Return top 10 suggestions

def add_import_to_file(file_path, class_name, class_index):
    """Add import statement to a file"""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the class is already imported
    existing_imports = get_existing_imports(content)
    import_statement = get_import_statement(class_name, class_index[class_name], file_path)
    
    for imp in existing_imports:
        if class_name in imp and import_statement in imp:
            print(f"{class_name} is already imported")
            return True
    
    # Add the import statement
    lines = content.split('\n')
    import_lines = []
    other_lines = []
    
    # Separate import lines from other content
    for line in lines:
        if line.startswith('from ') or line.startswith('import '):
            import_lines.append(line)
        else:
            other_lines.append(line)
    
    # Add the new import
    import_lines.append(import_statement)
    
    # Reconstruct the file content
    new_content = '\n'.join(sorted(import_lines)) + '\n\n' + '\n'.join(other_lines)
    
    # Write back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added import for {class_name} to {file_path}")
    return True

def interactive_mode():
    """Start interactive mode for auto-imports"""
    setup_django()
    project_root = get_project_root()
    index_file = project_root / '.class_index.json'
    
    if not index_file.exists():
        print("Class index not found. Generating...")
        class_index = generate_class_index()
    else:
        class_index = load_class_index(index_file)
    
    print(f"Loaded {len(class_index)} classes. Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input("Enter class name (or partial name): ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            suggestions = get_suggestions(class_index, user_input)
            if not suggestions:
                print("No classes found with that name")
                continue
            
            print("Suggestions:")
            for i, cls in enumerate(suggestions, 1):
                print(f"{i}. {cls}")
            
            selection = input("Select a class (number) or press Enter to skip: ").strip()
            if selection and selection.isdigit():
                idx = int(selection) - 1
                if 0 <= idx < len(suggestions):
                    selected_class = suggestions[idx]
                    file_path = input("Enter file path to add import to: ").strip()
                    if file_path:
                        file_path = os.path.join(project_root, file_path)
                        add_import_to_file(file_path, selected_class, class_index)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'generate-index':
        generate_class_index()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()