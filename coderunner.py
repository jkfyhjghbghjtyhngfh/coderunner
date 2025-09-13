import subprocess
import sys
import os
from flask import Flask, render_template_string, request

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

def run_code(language, file_path):
    if language not in LANG_COMMANDS:
        print(f"Unsupported language: {language}")
        return
    cmd = LANG_COMMANDS[language](file_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except Exception as e:
        print(f"Error running code: {e}")

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
                    <option value="python" {% if language == 'python' %}selected{% endif %}>Python</option>
                    <option value="javascript" {% if language == 'javascript' %}selected{% endif %}>JavaScript</option>
                    <option value="bash" {% if language == 'bash' %}selected{% endif %}>Bash</option>
                    <option value="batch" {% if language == 'batch' %}selected{% endif %}>Batch</option>
                    <option value="html" {% if language == 'html' %}selected{% endif %}>HTML</option>
                    <option value="css" {% if language == 'css' %}selected{% endif %}>CSS</option>
                </select>
            </div>
            <div>
                <label for="code" class="block font-semibold mb-1">Code:</label>
                <textarea name="code" id="code" rows="10" class="w-full p-2 border rounded font-mono">{% if code %}{{ code }}{% endif %}</textarea>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-bold">Run</button>
        </form>
        <div class="mt-8">
            <div class="flex border-b mb-4">
                <button id="outputTab" class="px-4 py-2 font-semibold text-blue-600 border-b-2 border-blue-600 focus:outline-none" onclick="showTab('output')">Output</button>
                <button id="previewTab" class="px-4 py-2 font-semibold text-gray-600 border-b-2 border-transparent focus:outline-none" onclick="showTab('preview')">Preview</button>
            </div>
            <div id="outputPanel">
                {# Running Command box hidden #}
                {% if output %}
                <div>
                    <h3 class="text-xl font-semibold mb-2 text-green-700">Output:</h3>
                    <pre class="bg-gray-900 text-green-300 p-4 rounded overflow-x-auto">{{ output }}</pre>
                </div>
                {% endif %}
            </div>
            <div id="previewPanel" style="display:none;">
                <h3 class="text-xl font-semibold mb-2 text-purple-700">Preview:</h3>
                {% if language in ['html', 'css'] and preview %}
                    <iframe srcdoc="{{ preview|safe }}" class="w-full h-64 border rounded"></iframe>
                {% elif preview %}
                    <pre class="bg-gray-900 text-purple-300 p-4 rounded overflow-x-auto">{{ preview }}</pre>
                {% else %}
                    <div class="text-gray-500">No code to preview.</div>
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

def flask_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        output = ''
        cmd_str = ''
        preview = ''
        language = ''
        code = ''
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
                preview = code
            except Exception as e:
                output = f'Error: {e}'
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        return render_template_string(HTML, output=output, cmd=cmd_str, preview=preview, language=language, code=code)

    app.run(host='0.0.0.0', port=6767, debug=True)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        lang = sys.argv[1].lower()
        file_path = sys.argv[2]
        run_code(lang, file_path)
    elif len(sys.argv) == 1:
        flask_app()
    else:
        print("Interactive mode: type your code block below. End with a line containing only 'END'.")
        lang = input("Enter language (python, javascript, bash, batch, html, css): ").strip().lower()
        print("Enter your code block:")
        code_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            code_lines.append(line)
        code = '\n'.join(code_lines)
        ext = EXT_MAP.get(lang, '.txt')
        temp_file = f'temp_code{ext}'
        with open(temp_file, 'w') as f:
            f.write(code)
        run_code(lang, temp_file)
        os.remove(temp_file)
