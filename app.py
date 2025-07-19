import os
import logging
from flask import Flask, render_template, request, jsonify
from utils.summarizer import summarize_text, detect_language

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)  # This line creates the 'app' variable that main.py is trying to import
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Simple test route to verify template rendering"""
    return render_template('test.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """API endpoint to summarize text"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract parameters
        text = data.get('text', '')
        ratio = data.get('ratio', 0.3)
        language = data.get('language', 'auto')
        
        # Validate parameters
        if not text or len(text) < 10:
            return jsonify({"error": "Text is too short to summarize"}), 400
        
        if not isinstance(ratio, (int, float)) or ratio <= 0 or ratio >= 1:
            return jsonify({"error": "Invalid ratio value"}), 400
        
        # Auto-detect language if needed
        if language == 'auto':
            language = detect_language(text)
        
        # Generate summary
        logger.debug(f"Summarizing text with ratio {ratio} and language {language}")
        summary = summarize_text(text, ratio, language)
        
        # Return summary
        return jsonify({"summary": summary, "language": language})
    
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error occurred"}), 500