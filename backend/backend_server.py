from flask import Flask, request, Response, stream_with_context
import subprocess
import json

app = Flask(__name__)

def stream_model_output(prompt):
    # Ollama start, pipes to run real-time response to front-end
    process = subprocess.Popen(
        ["ollama", "run", "gemma2:2b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Write the prompt to stdin
    process.stdin.write(prompt)
    process.stdin.close()
    
    # Read and yield output line by line
    while True:
        output_line = process.stdout.readline()
        if output_line == '' and process.poll() is not None:
            break
        if output_line:
            # Yield each line as a server-sent event
            yield f"data: {json.dumps({'response': output_line.strip()})}\n\n"
    
    # Error check
    if process.returncode != 0:
        error_message = process.stderr.read()
        yield f"data: {json.dumps({'error': error_message})}\n\n"

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

    # Return a streaming response
    return Response(
        stream_with_context(stream_model_output(prompt)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
