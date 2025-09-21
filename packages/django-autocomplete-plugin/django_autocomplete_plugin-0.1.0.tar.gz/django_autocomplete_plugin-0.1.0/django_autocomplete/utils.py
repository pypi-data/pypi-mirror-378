import inspect
import importlib
from django.apps import apps
from .models import AutocompleteEntry

def discover_models():
    """Discover all Django models"""
    entries = []
    for model in apps.get_models():
        entries.append({
            'name': model.__name__,
            'module_path': model.__module__,
            'class_name': model.__name__,
            'is_function': False,
            'description': f"Django Model: {model.__name__}"
        })
    return entries

def discover_project_modules(project_name):
    """Discover custom modules in the project"""
    entries = []
    try:
        project_module = importlib.import_module(project_name)
        for name, obj in inspect.getmembers(project_module):
            if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith('_'):
                entries.append({
                    'name': name,
                    'module_path': obj.__module__,
                    'class_name': obj.__name__ if inspect.isclass(obj) else '',
                    'is_function': inspect.isfunction(obj),
                    'description': f"{'Function' if inspect.isfunction(obj) else 'Class'}: {name}"
                })
    except ImportError:
        pass
    return entries

def update_autocomplete_data():
    """Update autocomplete database entries"""
    AutocompleteEntry.objects.all().delete()
    
    # Add Django models
    for model_data in discover_models():
        AutocompleteEntry.objects.get_or_create(**model_data)
    
    # Add project-specific modules (assuming project name is in settings)
    from django.conf import settings
    project_name = settings.SETTINGS_MODULE.split('.')[0]
    for module_data in discover_project_modules(project_name):
        AutocompleteEntry.objects.get_or_create(**module_data)