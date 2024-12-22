from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Define the endpoint for interacting with the model
@app.route('/api/v1/query', methods=['POST'])
def query_model():
    # Parse the input JSON
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Call Ollama using subprocess to execute the model with the prompt
    try:
        result = subprocess.run(
            ["ollama", "run", "qwen:0.5b"], # Replace with the model you want
            input=prompt,  # Pass the prompt as stdin input
            text=True,
            capture_output=True
        )

        # Check if the model executed successfully
        if result.returncode != 0:
            return jsonify({"error": "Error running model", "message": result.stderr}), 500

        # Send the model's output as the response
        return jsonify({"response": result.stdout.strip()})

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Expose API on port 5000

