from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [os.getenv("REACT_URL", "http://localhost:5173")],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'ok', 'service': 'ML Pipeline API'}, 200

@app.route('/api/pipeline/route', methods=['POST'])
def document_router():
    """Pipeline 0: Document Router"""
    return {'message': 'Document routing not implemented yet'}, 501

@app.route('/api/pipeline/extract', methods=['POST'])
def knowledge_extraction():
    """Pipeline 1: Knowledge Extraction"""
    return {'message': 'Knowledge extraction not implemented yet'}, 501

@app.route('/api/pipeline/classify', methods=['POST'])
def domain_classification():
    """Pipeline 2: Domain Classification"""
    return {'message': 'Domain classification not implemented yet'}, 501

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
