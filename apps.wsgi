import sys, os
print(os.path.dirname(__file__))
sys.path.insert(0, "C:\Apache24\htdocs\InAnalysisBackend")
from apps import app
application = app