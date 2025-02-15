from flask import Flask, request, Response, stream_with_context
import subprocess
import json
import shlex
import os
import time
import signal

app = Flask(__name__)

# Define the directory and path for the ollama binary.
OLLAMA_DIR = os.path.expanduser("~/ollama")
OLLAMA_BIN = os.path.join(OLLAMA_DIR, "ollama")

# Keep track of the background serve process
ollama_server_proc = None

def start_ollama_server():
    """
    Start the ollama serve process if not already running.
    This runs "./ollama serve" in the ~/ollama directory.
    """
    global ollama_server_proc
    if ollama_server_proc is None or ollama_server_proc.poll() is not None:
        print("Starting ollama server...")
        # Start the ollama serve process in background
        ollama_server_proc = subprocess.Popen(
            [OLLAMA_BIN, "serve"],
            cwd=OLLAMA_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # To start the process in a new group
        )
        # Give the server some time to start up
        time.sleep(2)
    else:
        print("Ollama server is already running.")

def stream_model_output(prompt):
    # Ensure the ollama server is running
    start_ollama_server()

    # Sanitize the prompt to prevent command injection
    safe_prompt = shlex.quote(prompt)

    # Prepare the command for running the model.
    # It uses the ollama binary from ~/ollama and runs the model "gemma2:2b".
    cmd = [OLLAMA_BIN, "run", "gemma2:2b"]

    # Start the subprocess with the proper working directory
    process = subprocess.Popen(
        cmd,
        cwd=OLLAMA_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

    # Write the sanitized prompt to stdin and close it
    process.stdin.write(safe_prompt + "\n")
    process.stdin.close()

    # Read and yield output line by line
    full_response = ""
    while True:
        output_line = process.stdout.readline()
        if output_line == '' and process.poll() is not None:
            break
        if output_line:
            # Append the new output, clean it up and print live
            full_response += output_line.strip() + " "
            print(output_line.strip())

            # Yield the current output as a server-sent event
            yield f"data: {json.dumps({'response': full_response.strip()})}\n\n"

    # Check if the process ended with an error and yield the error message if so
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

    # Return a streaming response for server-sent events
    return Response(
        stream_with_context(stream_model_output(prompt)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

def cleanup():
    """
    Terminate the ollama server process if running.
    """
    global ollama_server_proc
    if ollama_server_proc and ollama_server_proc.poll() is None:
        print("Terminating ollama server...")
        os.killpg(os.getpgid(ollama_server_proc.pid), signal.SIGTERM)

if __name__ == '__main__':
    try:
        # Start the ollama server (if not already running)
        start_ollama_server()
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        # Ensure the ollama server is cleaned up on exit
        cleanup()
