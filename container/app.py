from flask import Flask, request, jsonify, send_from_directory
import openai
import os

# ============================================================================
# CONFIGURATION - Modify these values to customize the template
# ============================================================================

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Get API key from environment variable (injected by kubelet stored via kubernetes secret)
OPENAI_MODEL = "gpt-3.5-turbo"  # Model to use for completions

# Endpoint Configuration
API_ENDPOINT = '/translate'  # API endpoint path (must match the one in index.html) I couldn't think of a good way to make this more of a general example so I am using "translate" because that is what the app in my screenshot is doing
REQUEST_PROPERTY = 'text'  # Property name in the request JSON (must match the one in index.html)
RESPONSE_PROPERTY = 'translatedText'  # Property name in the response JSON (must match the one in index.html)

# Prompt Configuration
PROMPT_TEMPLATE = "WHATEVER YOU WANT OPENAI TO DO WITH THE INPUT TEXT: {input_text}"  # Template for the prompt

# Server Configuration
HOST = '0.0.0.0'  # Host to run the server on
PORT = 5000  # Port to run the server on

# ============================================================================
# APPLICATION - The core functionality (you shouldn't need to modify this)
# ============================================================================

app = Flask(__name__)

# Initialize the OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route(API_ENDPOINT, methods=['POST'])
def process_request():
    """Process the API request based on the configured endpoint"""
    # Get the request data
    data = request.get_json()
    input_text = data.get(REQUEST_PROPERTY, '')
    
    if not input_text:
        return jsonify({"error": f"No {REQUEST_PROPERTY} provided in request"}), 400

    try:
        # Call the OpenAI API with the configured prompt
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": PROMPT_TEMPLATE.format(input_text=input_text)}
            ]
        )
        
        # Extract and return the response
        output_from_openai = response.choices[0].message.content.strip()
        return jsonify({RESPONSE_PROPERTY: output_from_openai})
    
    except openai.error.OpenAIError as e:
        # Handle OpenAI API errors
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        # Handle other unexpected errors
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    print(f"Starting server on {HOST}:{PORT}")
    print(f"API endpoint: {API_ENDPOINT}")
    app.run(host=HOST, port=PORT)
