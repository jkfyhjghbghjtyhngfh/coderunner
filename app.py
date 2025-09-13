from flask import Flask, render_template_string, request
import subprocess
import os

app = Flask(__name__)

LANG_COMMANDS = {
    'python': lambda file: ['python3', file],
    'javascript': lambda file: ['node', file],
    'bash': lambda file: ['bash', file],
    'batch': lambda file: ['cmd', '/c', file],
    'html': lambda file: ['xdg-open', file],
    'css': lambda file: ['xdg-open', file],
}

EXT_MAP = {
    'python': '.py',
    'javascript': '.js',
    'bash': '.sh',
    'batch': '.bat',
    'html': '.html',
    'css': '.css',
}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Code Runner</title>
    <style>
        .cmd-box { background: #f4f4f4; border: 1px solid #ccc; padding: 8px; margin-bottom: 16px; font-family: monospace; }
    </style>
</head>
<body>
    <h2>Code Runner</h2>
    <form method="post">
        <label for="language">Language:</label>
        <select name="language" id="language">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="bash">Bash</option>
            <option value="batch">Batch</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
        </select><br><br>
        <label for="code">Code:</label><br>
        <textarea name="code" id="code" rows="10" cols="60"></textarea><br><br>
        <button type="submit">Run</button>
    </form>
    {% if cmd %}
    <div class="cmd-box">
        <strong>Running Command:</strong><br>
        <pre>{{ cmd }}</pre>
    </div>
    {% endif %}
    {% if output %}
    <h3>Output:</h3>
    <pre>{{ output }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    cmd_str = ''
    if request.method == 'POST':
        language = request.form['language']
        code = request.form['code']
        ext = EXT_MAP.get(language, '.txt')
        temp_file = f'temp_code{ext}'
        with open(temp_file, 'w') as f:
            f.write(code)
        cmd = LANG_COMMANDS.get(language, lambda f: ['cat', f])(temp_file)
        cmd_str = ' '.join(cmd)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout + (('\n' + result.stderr) if result.stderr else '')
        except Exception as e:
            output = f'Error: {e}'
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    return render_template_string(HTML, output=output, cmd=cmd_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
