from app import create_app
from flask_cors import CORS
import os

app = create_app()
CORS(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Changed default to 8080
    app.run(host='0.0.0.0', port=port, debug=False)
