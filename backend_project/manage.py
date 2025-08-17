#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

#!/usr/bin/env python
# import os
# import sys
# import pathlib

# if __name__ == "__main__":
#     # Add the parent directory to Python path so it can find backend_project module
#     current_dir = pathlib.Path(__file__).parent.absolute()
#     parent_dir = current_dir.parent
    
#     if str(parent_dir) not in sys.path:
#         sys.path.insert(0, str(parent_dir))
    
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
    
#     execute_from_command_line(sys.argv)