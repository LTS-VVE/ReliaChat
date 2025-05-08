from flask import Flask, request, Response, stream_with_context
import subprocess
import json
import shlex
import time

app = Flask(__name__)

def stream_model_output(prompt):
    # Sanitize the prompt to prevent command injection
    safe_prompt = shlex.quote(prompt)
    
    # Start the subprocess to run the command
    process = subprocess.Popen(
        ["ollama", "run", "smollm:135m"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered for character streaming
    )
    
    # Write the sanitized prompt to stdin and flush immediately
    process.stdin.write(safe_prompt + "\n")
    process.stdin.flush()
    process.stdin.close()
    
    # Read character by character
    buffer = ""
    while True:
        char = process.stdout.read(1)
        
        if not char and process.poll() is not None:
            break
            
        if char:
            buffer += char
            
            # Send individual characters for lightning-fast streaming
            yield f"data: {json.dumps({'response': char})}\n\n"
    
    # If an error occurred, yield the error message immediately
    if process.returncode != 0:
        error_message = process.stderr.read()
        yield f"data: {json.dumps({'error': error_message.strip()})}\n\n"

@app.route('/api/v1/query', methods=['POST'])
def query_model():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return Response(
            json.dumps({"error": "No prompt provided"}),
            status=400,
            mimetype='application/json'
        )
    
    # Return a streaming response with headers for immediate streaming
    return Response(
        stream_with_context(stream_model_output(prompt)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'X-Accel-Buffering': 'no'  # Disable proxy buffering
        }
    )

@app.route('/api/v1/status', methods=['GET'])
def status():
    status_data = {
        "status": "connected",
        "model_name": "gemma:2b"
    }
    return Response(
        json.dumps(status_data),
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
