from flask import Flask, request, Response, stream_with_context
import subprocess
import json

app = Flask(__name__)

def stream_model_output(prompt):
    try:
        process = subprocess.Popen(
            ["./ollama", "run", "gemma:2b"],  # Changed to local binary
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd="/data/data/com.termux/files/home/ollama"  # Absolute path to ollama dir
        )

        process.stdin.write(prompt + "\n")
        process.stdin.flush()
        process.stdin.close()

        while True:
            output_line = process.stdout.readline()
            if not output_line and process.poll() is not None:
                break
            if output_line:
                yield f"data: {json.dumps({'response': output_line.strip()})}\n\n"

        if process.returncode != 0:
            error = process.stderr.read()
            yield f"data: {json.dumps({'error': error})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

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
    app.run(host='0.0.0.0', port=5000)
