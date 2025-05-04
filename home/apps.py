from django.apps import AppConfig

class HomeConfig(AppConfig):
    """
    Configuration class for the Home application.
    Handles application-specific configurations and signals.
    
    This application manages:
    - User authentication and roles (Owner, Manager, Sales Agent)
    - Branch management
    - Stock inventory
    - Sales transactions
    - Credit management
    - Receipt generation
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
