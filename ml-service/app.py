from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pipeline0.router import route_document

load_dotenv()

app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, resources={
    r"/pipeline0/*": {
        "origins": [os.getenv("LARAVEL_URL", "http://localhost:8000")],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
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


@app.route('/pipeline0/route', methods=['POST'])
def document_router():
    """
    Pipeline 0: Document Router
    POST /pipeline0/route
    
    Receives a file (PDF, CSV, or Excel) and routes it to appropriate pipelines.
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'No file provided',
                'log': ['❌ No file provided in request']
            }, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'No file selected',
                'log': ['❌ No file selected']
            }, 400
        
        # Get file content
        file_content = file.read()
        
        # Determine file type from extension
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            file_type = 'pdf'
        elif filename.endswith('.csv'):
            file_type = 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            file_type = 'excel'
        else:
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'Unsupported file type',
                'log': [f'❌ Unsupported file type: {filename}']
            }, 400
        
        # Route the document
        result = route_document(file.filename, file_content, file_type)
        return result, 200
    
    except Exception as e:
        return {
            'file_type': 'unknown',
            'routing': 'rejected',
            'pages': 0,
            'text_preview': '',
            'reason': str(e),
            'log': [f'❌ Server error: {str(e)}']
        }, 500


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
