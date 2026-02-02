from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# Import nurse conversation logic
from nurse_logic import nurse_turn

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint for chat messages.
    Expects JSON: {
        "yaml_path": "Richard_Crowther",
        "initial_prompt": "Hi doctor, please could you review...",
        "messages": [{"role": "user/assistant", "content": "..."}]
    }
    Returns JSON: { "response": "..." }
    """
    try:
        data = request.json
        yaml_path = data.get('yaml_path')
        initial_prompt = data.get('initial_prompt')
        messages = data.get('messages', [])

        if not yaml_path:
            return jsonify({'error': 'No yaml_path provided'}), 400

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Get the last user message (doctor's question)
        doctor_question = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                doctor_question = msg.get('content')
                break

        if not doctor_question:
            return jsonify({'error': 'No user message found'}), 400

        # Call the nurse_turn function
        nurse_response = nurse_turn(
            client=client,
            yaml_path=yaml_path,
            doctor_question=doctor_question,
            initial_nurse_bleep_request=initial_prompt
        )

        return jsonify({
            'response': nurse_response
        })

    except FileNotFoundError as e:
        print(f"YAML file not found: {str(e)}")
        return jsonify({'error': f'Patient data file not found: {str(e)}'}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)