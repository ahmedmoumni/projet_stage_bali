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
        print("📥 [Pipeline0] Request received")
        
        # Check if file is in request
        if 'file' not in request.files:
            print("❌ [Pipeline0] No file in request.files")
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'No file provided',
                'log': ['❌ No file provided in request']
            }, 400
        
        file = request.files['file']
        print(f"✅ [Pipeline0] File received: {file.filename}")
        
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
        print(f"✅ [Pipeline0] File size: {len(file_content)} bytes")
        
        # Determine file type from extension
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            file_type = 'pdf'
        elif filename.endswith('.csv'):
            file_type = 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            file_type = 'excel'
        else:
            print(f"❌ [Pipeline0] Unsupported file type: {filename}")
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'Unsupported file type',
                'log': [f'❌ Unsupported file type: {filename}']
            }, 400
        
        print(f"✅ [Pipeline0] File type detected: {file_type}")
        
        # Route the document
        print(f"🔄 [Pipeline0] Calling route_document()")
        result = route_document(file.filename, file_content, file_type)
        
        data = result.get('data', {})
        if isinstance(data, dict):
            rows_count = len(data.get('rows', []))
            headers = data.get('headers', [])
            print(f"✅ [Pipeline0] Result: routing={result.get('routing')}, file_type={result.get('file_type')}, rows={rows_count}, headers={len(headers)}")
        else:
            print(f"✅ [Pipeline0] Result: routing={result.get('routing')}, file_type={result.get('file_type')}")
        
        return result, 200
    
    except Exception as e:
        print(f"❌ [Pipeline0] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
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
    Pipeline 2: Classify Items
    POST /pipeline2/classify
    
    Three modes:
    1. New structure (from P0): {'data': {'headers': [...], 'rows': [...]}, 'source': '...'}
    2. Legacy items list: {'items': [texts], 'source': '...'}
    3. Database: no data
    """
    try:
        from pipeline2.classifier import classifier
        
        data = request.get_json() or {}
        source = data.get('source', 'database')
        
        # MODE 1: New structure (Pipeline 0 direct → Pipeline 2)
        if 'data' in data and isinstance(data['data'], dict):
            structured_data = data['data']
            headers = structured_data.get('headers', [])
            rows = structured_data.get('rows', [])
            subject_column = structured_data.get('subject_column')
            relation_columns = structured_data.get('relation_columns', [])
            
            if not headers or not rows:
                return {
                    'status': 'error',
                    'message': 'Data structure invalid: missing headers or rows',
                    'classified': 0,
                    'predictions': []
                }, 400
            
            predictions = []
            domain_dist = {}
            
            # If subject_column not provided, use first column
            if not subject_column:
                subject_column = headers[0]
            if not relation_columns:
                relation_columns = headers[1:]
            
            for row in rows:
                # Get subject from first column
                subject = str(row.get(subject_column, 'unknown'))
                
                # Create ONE FACT per relation column
                # Each relation becomes a separate fact
                for relation_col in relation_columns:
                    relation_value = str(row.get(relation_col, ''))
                    
                    # Create fact item for classification (dual-algorithm logic)
                    fact_item = {
                        'type': 'fact',
                        'subject': subject,
                        'relation': f'has_{relation_col.lower()}',  # e.g., 'has_population'
                        'values': relation_value
                    }
                    
                    # Classify using dual-algorithm approach with confidence consultation
                    try:
                        predictions_result = classifier.predict([fact_item])
                        if predictions_result and len(predictions_result) > 0:
                            pred = predictions_result[0]
                            domain = pred.get('predicted_domain', 'unknown')
                            confidence = pred.get('confidence', 0)
                            status = pred.get('status', 'pending_review')
                            algorithm_used = pred.get('algorithm_used', 'unknown')
                            tfidf_text = pred.get('text', '')
                        else:
                            domain = 'unknown'
                            confidence = 0
                            status = 'pending_review'
                            algorithm_used = 'unknown'
                            tfidf_text = ''
                    except Exception as e:
                        print(f"❌ Classification error: {str(e)}")
                        domain = 'unknown'
                        confidence = 0
                        status = 'pending_review'
                        algorithm_used = 'unknown'
                        tfidf_text = ''
                    
                    # Create fact for this relation
                    pred_obj = {
                        'subject': subject,
                        'relation': f'has_{relation_col.lower()}',  # e.g., 'has_population'
                        'relation_column': relation_col,
                        'relation_value': relation_value,
                        'text': tfidf_text,
                        'domain': domain,
                        'confidence': float(confidence),
                        'status': status,
                        'algorithm_used': algorithm_used,
                        'row_data': {relation_col: relation_value},  # Single value
                        'headers': [relation_col]
                    }
                    
                    predictions.append(pred_obj)
                    domain_dist[domain] = domain_dist.get(domain, 0) + 1
            
            return {
                'status': 'success',
                'source': source,
                'classified': len(predictions),
                'domain_distribution': domain_dist,
                'predictions': predictions
            }, 200
        
        # MODE 2: Legacy items list
        items = data.get('items')
        if items and isinstance(items, list) and len(items) > 0:
            classified_items = []
            domain_dist = {}
            
            for item_text in items:
                text = str(item_text) if item_text else ""
                
                if text.strip():
                    try:
                        prediction = classifier.predict([text])
                        if prediction and len(prediction) > 0:
                            domain = prediction[0].get('predicted_domain', 'unknown')
                            confidence = prediction[0].get('confidence', 0)
                        else:
                            domain = 'unknown'
                            confidence = 0
                    except Exception as classify_error:
                        domain = 'unknown'
                        confidence = 0
                else:
                    domain = 'unknown'
                    confidence = 0
                
                classified_items.append({
                    'text': text,
                    'domain': domain,
                    'confidence': float(confidence)
                })
                
                domain_dist[domain] = domain_dist.get(domain, 0) + 1
            
            return {
                'status': 'success',
                'source': source,
                'classified': len(classified_items),
                'domain_distribution': domain_dist,
                'predictions': classified_items
            }, 200
        
        # MODE 3: Classify all unclassified from database
        result = classify_and_update()
        return result, 200
    
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'message': str(e),
            'classified': 0,
            'error_trace': traceback.format_exc()
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


@app.route('/orchestrate', methods=['POST'])
def orchestrate():
    """
    Complete Pipeline Orchestration
    POST /orchestrate
    
    Receives a file and executes the complete pipeline:
    1. Pipeline 0: Routes document (text extraction + routing decision)
    2. Based on routing:
       - rejected: Stop, return document_log
       - pipeline1/ocr_then_pipeline1: Run Pipeline 1 → Pipeline 2
       - pipeline2_direct: Run Pipeline 2 directly with CSV/Excel data
    
    Returns combined results from all executed pipelines.
    """
    try:
        if 'file' not in request.files:
            return {
                'status': 'error',
                'message': 'No file provided',
                'orchestration_log': ['❌ No file provided']
            }, 400
        
        file = request.files['file']
        visibility = request.form.get('visibility', 'private')
        
        if file.filename == '':
            return {
                'status': 'error',
                'message': 'No file selected',
                'orchestration_log': ['❌ No file selected']
            }, 400
        
        orchestration_log = []
        combined_result = {
            'status': 'success',
            'visibility': visibility,
            'orchestration_log': orchestration_log,
            'pipeline0_result': None,
            'pipeline1_result': None,
            'pipeline2_result': None,
            'summary': {
                'routing': 'unknown',
                'file_type': 'unknown',
                'pages': 0,
                'rules_extracted': 0,
                'facts_extracted': 0,
                'domain_distribution': {}
            }
        }
        
        # STEP 1: Run Pipeline 0 - Document Router
        orchestration_log.append(f"📄 Processing file: {file.filename}")
        file_content = file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            file_type = 'pdf'
        elif filename.endswith('.csv'):
            file_type = 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            file_type = 'excel'
        else:
            orchestration_log.append("❌ Unsupported file type")
            combined_result['status'] = 'error'
            return combined_result, 400
        
        orchestration_log.append(f"🔍 Running Pipeline 0 - Document Router")
        pipeline0_result = route_document(file.filename, file_content, file_type)
        combined_result['pipeline0_result'] = pipeline0_result
        
        routing = pipeline0_result.get('routing', 'rejected')
        file_type_detected = pipeline0_result.get('file_type', 'unknown')
        pages = pipeline0_result.get('pages', 0)
        
        combined_result['summary']['routing'] = routing
        combined_result['summary']['file_type'] = file_type_detected
        combined_result['summary']['pages'] = pages
        
        orchestration_log.append(f"✅ Pipeline 0: routing={routing}, file_type={file_type_detected}")
        
        # STEP 2: Route to appropriate pipeline(s)
        if routing == 'rejected':
            orchestration_log.append("🛑 Document rejected - stopping orchestration")
            combined_result['summary']['rules_extracted'] = 0
            combined_result['summary']['facts_extracted'] = 0
        
        elif routing in ['pipeline1', 'ocr_then_pipeline1']:
            # Run Pipeline 1 - Extract rules and facts from text
            text = pipeline0_result.get('text', '')
            orchestration_log.append(f"🔄 Running Pipeline 1 - Knowledge Extraction")
            
            pipeline1_result = extract_pipeline1(text)
            combined_result['pipeline1_result'] = pipeline1_result
            
            rules_extracted = pipeline1_result.get('rules_extracted', 0)
            facts_extracted = pipeline1_result.get('facts_extracted', 0)
            combined_result['summary']['rules_extracted'] = rules_extracted
            combined_result['summary']['facts_extracted'] = facts_extracted
            
            orchestration_log.append(f"✅ Pipeline 1: {rules_extracted} rules, {facts_extracted} facts extracted")
            
            # Auto-run Pipeline 2 - Classify extracted items
            if rules_extracted > 0 or facts_extracted > 0:
                orchestration_log.append(f"🔄 Running Pipeline 2 - Domain Classification (auto-triggered)")
                pipeline2_result = classify_and_update()
                combined_result['pipeline2_result'] = pipeline2_result
                
                rules_classified = pipeline2_result.get('rules_classified', 0)
                facts_classified = pipeline2_result.get('facts_classified', 0)
                orchestration_log.append(f"✅ Pipeline 2: {rules_classified} rules, {facts_classified} facts classified")
                combined_result['summary']['domain_distribution'] = pipeline2_result.get('domain_distribution', {})
        
        elif routing == 'pipeline2_direct':
            # Structured data (CSV/Excel) - classify directly with Pipeline 2
            orchestration_log.append(f"🔄 Running Pipeline 2 - Direct Classification (CSV/Excel)")
            
            try:
                data = pipeline0_result.get('data', [])
                
                if not data or len(data) == 0:
                    orchestration_log.append("❌ No structured data extracted by Pipeline 0")
                    combined_result['status'] = 'partial_error'
                else:
                    # Data is already formatted as array of objects/rows from Pipeline 0
                    # Convert to texts for classification
                    texts = []
                    for row in data:
                        if isinstance(row, dict):
                            # Join all values into a text
                            row_text = ' '.join(str(v) for v in row.values() if v)
                        else:
                            row_text = str(row)
                        texts.append(row_text)
                    
                    # Classify each row
                    predictions = classify_pipeline2(texts)
                    combined_result['pipeline2_result'] = {
                        'status': 'success',
                        'source': 'pipeline0_direct',
                        'total_items': len(predictions),
                        'classified': len(predictions),
                        'predictions': predictions
                    }
                    
                    combined_result['summary']['facts_extracted'] = len(predictions)
                    combined_result['summary']['rules_extracted'] = 0
                    
                    # Count domain distribution
                    domain_dist = {}
                    for pred in predictions:
                        domain = pred.get('domain', 'unknown')
                        domain_dist[domain] = domain_dist.get(domain, 0) + 1
                    combined_result['summary']['domain_distribution'] = domain_dist
                    
                    orchestration_log.append(f"✅ Pipeline 2: {len(predictions)} items classified")
                    orchestration_log.append(f"   Domain distribution: {domain_dist}")
            
            except Exception as p2_error:
                orchestration_log.append(f"❌ Pipeline 2 error: {str(p2_error)}")
                combined_result['status'] = 'partial_error'
        
        orchestration_log.append("✅ Orchestration complete")
        return combined_result, 200
    
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'message': str(e),
            'orchestration_log': [f'❌ Server error: {str(e)}', traceback.format_exc()]
        }, 500


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
