"""
Pipeline 0: Document Router
Analyzes uploaded documents and routes them to appropriate pipelines
"""

import io
import os
from werkzeug.utils import secure_filename
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd


def extract_text_from_pdf(file_content):
    """
    Extract text from PDF file.
    Returns: (text, is_scanned, pages)
    """
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            pages = len(pdf.pages)
            text = ""
            
            # Try to extract text from all pages
            for page in pdf.pages:
                text += page.extract_text() or ""
            
            # If no text extracted, it might be a scanned PDF
            if not text or len(text.strip()) < 50:
                return text, True, pages
            
            return text, False, pages
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")


def extract_text_from_scanned_pdf(file_content):
    """
    Extract text from scanned PDF using OCR (pytesseract).
    Returns: (text, pages)
    """
    try:
        # Convert PDF to images and apply OCR
        from pdf2image import convert_from_bytes
        
        images = convert_from_bytes(file_content)
        text = ""
        
        for image in images:
            # Apply OCR to each image
            extracted = pytesseract.image_to_string(image)
            text += extracted + "\n"
        
        return text, len(images)
    except Exception as e:
        raise ValueError(f"Error applying OCR: {str(e)}")


def check_has_tables_with_columns(file_content):
    """
    Check if PDF has tables with more than 3 columns.
    Returns: boolean
    """
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if len(table[0]) > 3:  # Check first row column count
                            return True
        return False
    except Exception:
        return False


def extract_text_from_csv(file_content):
    """
    Extract text from CSV file.
    Returns: text
    """
    try:
        df = pd.read_csv(io.BytesIO(file_content))
        # Convert dataframe to readable text
        text = df.to_string()
        return text
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")


def extract_text_from_excel(file_content):
    """
    Extract text from Excel file.
    Returns: text
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        # Convert dataframe to readable text
        text = df.to_string()
        return text
    except Exception as e:
        raise ValueError(f"Error reading Excel: {str(e)}")


def route_document(filename, file_content, file_type):
    """
    Main routing function.
    
    Args:
        filename: Original filename
        file_content: File bytes content
        file_type: 'pdf', 'csv', or 'excel'
    
    Returns:
        dict with routing information and log
    """
    log = []
    
    try:
        log.append(f"✅ File received: {filename}")
        
        # Route based on file type
        if file_type == 'pdf':
            return route_pdf(filename, file_content, log)
        elif file_type == 'csv':
            return route_csv(filename, file_content, log)
        elif file_type == 'excel':
            return route_excel(filename, file_content, log)
        else:
            return {
                'file_type': 'unknown',
                'routing': 'rejected',
                'pages': 0,
                'text_preview': '',
                'reason': 'Unknown file type',
                'log': log + ['❌ Unknown file type']
            }
    
    except Exception as e:
        log.append(f"❌ Error processing file: {str(e)}")
        return {
            'file_type': 'unknown',
            'routing': 'rejected',
            'pages': 0,
            'text_preview': '',
            'reason': str(e),
            'log': log
        }


def route_pdf(filename, file_content, log):
    """Route PDF documents"""
    # Step 1: Try to extract text directly
    text, is_scanned, pages = extract_text_from_pdf(file_content)
    
    # Step 2: Content check - minimum 100 characters
    if len(text.strip()) < 100:
        if not is_scanned:
            log.append("✅ Content check passed (sufficient for OCR attempt)")
            # Try OCR on what looks like scanned
            try:
                ocr_text, ocr_pages = extract_text_from_scanned_pdf(file_content)
                if len(ocr_text.strip()) < 100:
                    log.append("❌ Document rejected — insufficient content even after OCR")
                    return {
                        'file_type': 'pdf_scanned',
                        'routing': 'rejected',
                        'pages': pages,
                        'text_preview': '',
                        'reason': 'insufficient content',
                        'log': log
                    }
                text = ocr_text
                pages = ocr_pages
                is_scanned = True
            except:
                log.append("❌ Document rejected — insufficient content")
                return {
                    'file_type': 'pdf_native',
                    'routing': 'rejected',
                    'pages': pages,
                    'text_preview': '',
                    'reason': 'insufficient content',
                    'log': log
                }
        else:
            log.append("✅ PDF detected as scanned — applying OCR")
            try:
                text, pages = extract_text_from_scanned_pdf(file_content)
                if len(text.strip()) < 100:
                    log.append("❌ Document rejected — insufficient content after OCR")
                    return {
                        'file_type': 'pdf_scanned',
                        'routing': 'rejected',
                        'pages': pages,
                        'text_preview': '',
                        'reason': 'insufficient content',
                        'log': log
                    }
            except Exception as e:
                log.append(f"❌ OCR failed: {str(e)}")
                return {
                    'file_type': 'pdf_scanned',
                    'routing': 'rejected',
                    'pages': pages,
                    'text_preview': '',
                    'reason': 'ocr_failed',
                    'log': log
                }
    
    log.append(f"✅ Content check passed ({len(text.strip())} chars)")
    
    # Step 2: Scan detection
    if is_scanned:
        log.append("✅ PDF detected as scanned")
        file_type_result = 'pdf_scanned'
        log.append("✅ OCR applied successfully")
        routing_result = 'ocr_then_pipeline1'
    else:
        log.append("✅ Native PDF detected — no OCR needed")
        file_type_result = 'pdf_native'
        
        # Step 3: Type detection - check for tables
        has_tables = check_has_tables_with_columns(file_content)
        if has_tables:
            log.append("✅ Structured data (tables) detected")
            routing_result = 'pipeline2_direct'
        else:
            log.append("✅ Narrative text detected")
            routing_result = 'pipeline1'
    
    text_preview = text[:200] if text else ""
    
    log.append(f"✅ Routed to {routing_result.replace('_', ' ').title()}")
    
    return {
        'file_type': file_type_result,
        'routing': routing_result,
        'pages': pages,
        'text_preview': text_preview,
        'log': log
    }


def route_csv(filename, file_content, log):
    """Route CSV documents"""
    try:
        text = extract_text_from_csv(file_content)
        log.append(f"✅ CSV file processed ({len(text)} chars)")
        log.append("✅ Structured data detected")
        log.append("✅ Routed to Pipeline 2")
        
        text_preview = text[:200] if text else ""
        
        return {
            'file_type': 'csv',
            'routing': 'pipeline2_direct',
            'pages': 1,
            'text_preview': text_preview,
            'log': log
        }
    except Exception as e:
        log.append(f"❌ Error processing CSV: {str(e)}")
        return {
            'file_type': 'csv',
            'routing': 'rejected',
            'pages': 0,
            'text_preview': '',
            'reason': str(e),
            'log': log
        }


def route_excel(filename, file_content, log):
    """Route Excel documents"""
    try:
        text = extract_text_from_excel(file_content)
        log.append(f"✅ Excel file processed ({len(text)} chars)")
        log.append("✅ Structured data detected")
        log.append("✅ Routed to Pipeline 2")
        
        text_preview = text[:200] if text else ""
        
        return {
            'file_type': 'excel',
            'routing': 'pipeline2_direct',
            'pages': 1,
            'text_preview': text_preview,
            'log': log
        }
    except Exception as e:
        log.append(f"❌ Error processing Excel: {str(e)}")
        return {
            'file_type': 'excel',
            'routing': 'rejected',
            'pages': 0,
            'text_preview': '',
            'reason': str(e),
            'log': log
        }
