import os
import importlib.util

# Import the app from live_portal/app.py directly
spec = importlib.util.spec_from_file_location("live_app", os.path.join(os.path.dirname(__file__), 'live_portal', 'app.py'))
live_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live_app)
app = live_app.app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
