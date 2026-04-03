import os
import sys

# Add live_portal directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'live_portal'))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
