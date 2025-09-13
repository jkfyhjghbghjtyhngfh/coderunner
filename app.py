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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Runner</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="bg-white shadow-lg rounded-lg p-8 w-full max-w-2xl">
        <h2 class="text-3xl font-bold mb-6 text-center text-blue-600">Code Runner</h2>
        <form method="post" class="space-y-4">
            <div>
                <label for="language" class="block font-semibold mb-1">Language:</label>
                <select name="language" id="language" class="w-full p-2 border rounded">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="bash">Bash</option>
                    <option value="batch">Batch</option>
                    <option value="html">HTML</option>
                    <option value="css">CSS</option>
                </select>
            </div>
            <div>
                <label for="code" class="block font-semibold mb-1">Code:</label>
                <textarea name="code" id="code" rows="10" class="w-full p-2 border rounded font-mono"></textarea>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-bold">Run</button>
        </form>
        <div class="mt-8">
            <div class="flex border-b mb-4">
                <button id="outputTab" class="px-4 py-2 font-semibold text-blue-600 border-b-2 border-blue-600 focus:outline-none" onclick="showTab('output')">Output</button>
                <button id="previewTab" class="px-4 py-2 font-semibold text-gray-600 border-b-2 border-transparent focus:outline-none" onclick="showTab('preview')">Preview</button>
            </div>
            <div id="outputPanel">
                {% if cmd %}
                <div class="bg-gray-50 border-l-4 border-blue-400 p-4 mb-4">
                    <span class="font-semibold text-blue-700">Running Command:</span>
                    <pre class="mt-2 text-sm text-gray-800">{{ cmd }}</pre>
                </div>
                {% endif %}
                {% if output %}
                <div>
                    <h3 class="text-xl font-semibold mb-2 text-green-700">Output:</h3>
                    <pre class="bg-gray-900 text-green-300 p-4 rounded overflow-x-auto">{{ output }}</pre>
                </div>
                {% endif %}
            </div>
            <div id="previewPanel" style="display:none;">
                {% if preview %}
                <h3 class="text-xl font-semibold mb-2 text-purple-700">Preview:</h3>
                <iframe srcdoc="{{ preview|safe }}" class="w-full h-64 border rounded"></iframe>
                {% else %}
                <div class="text-gray-500">No preview available for this language.</div>
                {% endif %}
            </div>
        </div>
    </div>
    <script>
        function showTab(tab) {
            document.getElementById('outputTab').classList.remove('text-blue-600', 'border-blue-600');
            document.getElementById('previewTab').classList.remove('text-blue-600', 'border-blue-600');
            document.getElementById('outputTab').classList.add('text-gray-600', 'border-transparent');
            document.getElementById('previewTab').classList.add('text-gray-600', 'border-transparent');
            document.getElementById('outputPanel').style.display = 'none';
            document.getElementById('previewPanel').style.display = 'none';
            if (tab === 'output') {
                document.getElementById('outputTab').classList.add('text-blue-600', 'border-blue-600');
                document.getElementById('outputPanel').style.display = 'block';
            } else {
                document.getElementById('previewTab').classList.add('text-blue-600', 'border-blue-600');
                document.getElementById('previewPanel').style.display = 'block';
            }
        }
        showTab('output');
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    cmd_str = ''
    preview = ''
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
            if language in ['html', 'css']:
                preview = code
        except Exception as e:
            output = f'Error: {e}'
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    return render_template_string(HTML, output=output, cmd=cmd_str, preview=preview)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
