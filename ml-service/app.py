from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from pipeline0.router import route_document
from pipeline1 import extract_pipeline1, init_db
from pipeline2 import train_pipeline2, classify_pipeline2, classify_and_update

load_dotenv()

app = Flask(__name__)

# Initialize Pipeline 1 database
try:
    init_db()
except Exception as e:
    print(f"⚠️  Database initialization: {str(e)}")

# Enable CORS for React frontend and Laravel backend
CORS(app, resources={
    r"/pipeline0/*": {
        "origins": [os.getenv("LARAVEL_URL", "http://localhost:8000")],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/pipeline1/*": {
        "origins": [os.getenv("LARAVEL_URL", "http://localhost:8000")],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/pipeline2/*": {
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
    """
    Pipeline 1: Knowledge Extraction
    POST /api/pipeline/extract
    
    Receives text from Pipeline 0 and extracts IF-THEN rules and facts.
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return {
                'error': 'No text provided',
                'rules_extracted': 0,
                'facts_extracted': 0,
                'log': ['❌ Missing text field']
            }, 400
        
        text = data['text']
        document_id = data.get('document_id', None)
        
        # Extract knowledge using Pipeline 1
        result = extract_pipeline1(text, document_id)
        
        return result, 200
    
    except Exception as e:
        return {
            'error': str(e),
            'rules_extracted': 0,
            'facts_extracted': 0,
            'log': [f'❌ Server error: {str(e)}']
        }, 500


@app.route('/pipeline2/train', methods=['POST'])
def train_classifiers():
    """
    Pipeline 2: Train Domain Classifiers
    POST /pipeline2/train
    
    Trains both Naive Bayes and Decision Tree classifiers on labeled data.
    Evaluates with stratified 5-fold cross-validation and selects the best.
    """
    try:
        result = train_pipeline2()
        return result, 200
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'success': False
        }, 500


@app.route('/pipeline2/classify', methods=['POST'])
def classify_items():
    """
    Pipeline 2: Classify Unclassified Items
    POST /pipeline2/classify
    
    Classifies all unclassified knowledge items from database and updates them.
    """
    try:
        result = classify_and_update()
        return result, 200
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'classified': 0
        }, 500


@app.route('/pipeline2/classify-file', methods=['POST'])
def classify_file():
    """
    Pipeline 2: Classify from File
    POST /pipeline2/classify-file
    
    Accepts CSV or Excel file with text column and returns domain classifications.
    Expected form data: file (multipart), text_column (default: 'text')
    """
    try:
        if 'file' not in request.files:
            return {
                'status': 'error',
                'message': 'No file provided',
                'classifications': []
            }, 400
        
        file = request.files['file']
        text_column = request.form.get('text_column', 'text')
        
        if file.filename == '':
            return {
                'status': 'error',
                'message': 'No file selected',
                'classifications': []
            }, 400
        
        # Parse file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return {
                'status': 'error',
                'message': 'Invalid file format. Supported: CSV, XLSX, XLS',
                'classifications': []
            }, 400
        
        if text_column not in df.columns:
            return {
                'status': 'error',
                'message': f"Column '{text_column}' not found in file",
                'available_columns': df.columns.tolist(),
                'classifications': []
            }, 400
        
        # Extract texts and classify
        texts = df[text_column].tolist()
        predictions = classify_pipeline2(texts)
        
        # Add original row index for reference
        for idx, pred in enumerate(predictions):
            pred['row_index'] = idx
        
        return {
            'status': 'success',
            'file': file.filename,
            'total_rows': len(texts),
            'classified': len(predictions),
            'classifications': predictions
        }, 200
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'classifications': []
        }, 500


@app.route('/pipeline2/stats', methods=['GET'])
def classification_stats():
    """
    Pipeline 2: Get Classification Statistics
    GET /pipeline2/stats
    
    Returns statistics on classified vs unclassified items in database.
    """
    try:
        from pipeline2.storage import storage
        stats = storage.get_classification_stats()
        return {
            'status': 'success',
            'statistics': stats
        }, 200
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500


@app.route('/pipeline2/evaluate', methods=['GET'])
def evaluation_results():
    """
    Pipeline 2: Get Evaluation Results
    GET /pipeline2/evaluate
    
    Returns stored evaluation results from last training.
    """
    try:
        from pipeline2.classifier import classifier
        results = classifier.get_evaluation_results()
        return {
            'status': 'success',
            'evaluation': results
        }, 200
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500


@app.route('/api/pipeline/classify', methods=['POST'])
def domain_classification():
    """Pipeline 2: Domain Classification"""
    return {'message': 'Domain classification not implemented yet'}, 501


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
