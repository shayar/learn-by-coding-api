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
frontend_url = os.getenv('FRONTEND_URL', 'https://learn-by-coding.netlify.app')
CORS(app, origins=[frontend_url], supports_credentials=True, allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

openai.api_key = os.getenv('OPENAI_API_KEY')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Run Python code
@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code')
    try:
        output = subprocess.check_output(['python', '-c', code], stderr=subprocess.STDOUT)
        return jsonify({'output': output.decode('utf-8')}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output.decode('utf-8')}), 400

# Generate a full explanation of the entire code
def openai_explain_code(code):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"Explain in detail what this entire Python code does:\n{code}",
            temperature=0.5,
            max_tokens=200
        )
        explanation = response.choices[0].text.strip()
        return explanation
    except RateLimitError:
        print("Rate limit exceeded. Falling back to spaCy.")
        return use_spacy_for_explanation(code)

# Fallback explanation using spaCy
def use_spacy_for_explanation(user_input):
    doc = nlp(user_input)
    explanation = f"This code consists of {len(doc)} tokens. Here's a simple description:\n"
    explanation += f"{' '.join([token.text for token in doc])}"
    return explanation

# Generate a human-readable diff that focuses on the new line addition
def new_line_difference(old_code, new_code):
    diff = difflib.ndiff(old_code.splitlines(), new_code.splitlines())
    added_lines = [line[2:] for line in diff if line.startswith('+ ')]
    if added_lines:
        return f"The new line added to the code: {', '.join(added_lines)}"
    return "No new lines were added."

# Unified route to explain and compare code
@app.route('/dynamic-explain', methods=['POST', 'OPTIONS'])
def dynamic_explain_code():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    data = request.json
    new_code = data.get('new_code')
    old_code = data.get('old_code', '')

    # Get full code explanation and the difference for the new line
    explanation = openai_explain_code(new_code)
    diff = new_line_difference(old_code, new_code)

    return jsonify({
        'explanation': explanation,
        'diff': diff
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
