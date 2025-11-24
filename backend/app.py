from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the summarization pipeline with BART model
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    logger.info("BART model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    summarizer = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': summarizer is not None
    }), 200

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    """
    Summarize text using Hugging Face BART model
    Expected JSON: {
        "text": "text to summarize",
        "min_length": 25,
        "max_length": 100
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()
        
        # Validate required fields
        if 'text' not in data or not data['text'].strip():
            return jsonify({
                'error': 'Text field is required and cannot be empty'
            }), 400

        text = data['text'].strip()
        min_length = data.get('min_length', 25)
        max_length = data.get('max_length', 100)

        # Validate length parameters
        if min_length < 10 or min_length > 200:
            return jsonify({
                'error': 'min_length must be between 10 and 200'
            }), 400

        if max_length < 20 or max_length > 500:
            return jsonify({
                'error': 'max_length must be between 20 and 500'
            }), 400

        if min_length >= max_length:
            return jsonify({
                'error': 'max_length must be greater than min_length'
            }), 400

        # Check text length
        if len(text.split()) < 30:
            return jsonify({
                'error': 'Text is too short to summarize. Please provide at least 30 words.'
            }), 400

        if len(text) > 5000:
            return jsonify({
                'error': 'Text is too long. Maximum 5000 characters allowed.'
            }), 400

        # Check if model is loaded
        if summarizer is None:
            return jsonify({
                'error': 'Model not loaded. Please try again later.'
            }), 503

        # Generate summary
        logger.info(f"Summarizing text with min_length={min_length}, max_length={max_length}")
        
        summary = summarizer(
            text,
            min_length=min_length,
            max_length=max_length,
            do_sample=False
        )

        return jsonify({
            'success': True,
            'summary': summary[0]['summary_text'],
            'original_length': len(text.split()),
            'summary_length': len(summary[0]['summary_text'].split()),
            'parameters': {
                'min_length': min_length,
                'max_length': max_length
            }
        }), 200

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return jsonify({
            'error': 'An error occurred during summarization. Please try again.',
            'details': str(e) if app.debug else None
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)