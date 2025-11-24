from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend to call backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global summarizer, lazily initialized
summarizer = None


def get_summarizer():
    """Lazily load the summarization pipeline."""
    global summarizer
    if summarizer is None:
        try:
            # You can switch to a lighter model if needed:
            # model_name = "sshleifer/distilbart-cnn-12-6"
            model_name = "facebook/bart-large-cnn"
            logger.info(f"Loading summarization model: {model_name}")
            summarizer = pipeline("summarization", model=model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            summarizer = None
    return summarizer


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    # Don't force model load here to keep health check fast
    return jsonify({
        "status": "healthy",
        "model_loaded": summarizer is not None
    }), 200


@app.route("/api/summarize", methods=["POST"])
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
        # Validate request type
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400

        data = request.get_json()

        # Validate required fields
        if "text" not in data or not str(data["text"]).strip():
            return jsonify({
                "error": "Text field is required and cannot be empty"
            }), 400

        text = str(data["text"]).strip()
        min_length = int(data.get("min_length", 25))
        max_length = int(data.get("max_length", 100))

        # Validate length parameters
        if min_length < 10 or min_length > 200:
            return jsonify({
                "error": "min_length must be between 10 and 200"
            }), 400

        if max_length < 20 or max_length > 500:
            return jsonify({
                "error": "max_length must be between 20 and 500"
            }), 400

        if min_length >= max_length:
            return jsonify({
                "error": "max_length must be greater than min_length"
            }), 400

        # Validate text length
        if len(text.split()) < 30:
            return jsonify({
                "error": "Text is too short to summarize. Please provide at least 30 words."
            }), 400

        if len(text) > 5000:
            return jsonify({
                "error": "Text is too long. Maximum 5000 characters allowed."
            }), 400

        # Ensure model is loaded
        model = get_summarizer()
        if model is None:
            return jsonify({
                "error": "Model not loaded. Please try again later."
            }), 503

        logger.info(f"Summarizing text with min_length={min_length}, max_length={max_length}")

        summary = model(
            text,
            min_length=min_length,
            max_length=max_length,
            do_sample=False
        )

        summary_text = summary[0]["summary_text"]

        return jsonify({
            "success": True,
            "summary": summary_text,
            "original_length": len(text.split()),
            "summary_length": len(summary_text.split()),
            "parameters": {
                "min_length": min_length,
                "max_length": max_length
            }
        }), 200

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return jsonify({
            "error": "An error occurred during summarization. Please try again.",
            "details": str(e) if app.debug else None
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
