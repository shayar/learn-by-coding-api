import openai
from flask import Flask, request, jsonify
import subprocess
import difflib
from flask_cors import CORS
from openai.error import RateLimitError
import os
import spacy
from spacy.cli import download

app = Flask(__name__)
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000/')
CORS(app, origins=[frontend_url])  # Enable CORS to allow frontend interaction

# Set your OpenAI API key here
openai.api_key = os.getenv('OPENAI_API_KEY')

# spaCy Model Handling
# Try to load the model, download if it's not available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Run Python code using subprocess
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code')

    try:
        # Execute the Python code
        output = subprocess.check_output(['python', '-c', code], stderr=subprocess.STDOUT)
        return jsonify({'output': output.decode('utf-8')}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output.decode('utf-8')}), 400

# Use OpenAI to dynamically explain code
def openai_explain_code(code):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"Explain the following Python code:\n{code}\nExplain it in a simple, detailed way.",
            temperature=0.7,
            max_tokens=150
        )
        explanation = response.choices[0].text.strip()
        return explanation
    except RateLimitError:
        print("Rate limit exceeded. Falling back to spaCy.")
        return use_spacy_for_explanation(code)
    
def use_spacy_for_explanation(user_input):
    doc = nlp(user_input)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    tokens = [token.text for token in doc]
    
    explanation = {
        "entities": entities,
        "tokens": tokens,
        "summary": f"Found {len(entities)} entities and {len(tokens)} tokens in the input."
    }
    
    return {"explanation": explanation}

# Route to explain the code using OpenAI
@app.route('/dynamic-explain', methods=['POST'])
def dynamic_explain_code():
    data = request.json
    new_code = data.get('new_code')

    explanation = openai_explain_code(new_code)

    return jsonify({'explanation': explanation}), 200

# Route to compare old and new code, explain the difference and its impact
@app.route('/explain-impact', methods=['POST'])
def explain_code_impact():
    data = request.json
    old_code = data.get('old_code')
    new_code = data.get('new_code')

    # Compare old and new code
    diff = difflib.unified_diff(old_code.splitlines(), new_code.splitlines(), lineterm='')
    diff_str = '\n'.join(diff)

    # Use OpenAI to explain the new code
    impact = openai_explain_code(new_code)

    return jsonify({'diff': diff_str, 'impact': impact}), 200

if __name__ == '__main__':
    app.run(debug=True)
