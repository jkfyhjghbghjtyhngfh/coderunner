import subprocess
import sys
import os

LANG_COMMANDS = {
    'python': lambda file: ['python3', file],
    'java': lambda file: ['javac', file] if file.endswith('.java') else ['java', file],
    'bash': lambda file: ['bash', file],
    'batch': lambda file: ['cmd', '/c', file],
    'html': lambda file: ['xdg-open', file],
    'css': lambda file: ['xdg-open', file],
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

if __name__ == "__main__":
    if len(sys.argv) == 3:
        lang = sys.argv[1].lower()
        file_path = sys.argv[2]
        run_code(lang, file_path)
    else:
        print("Interactive mode: type your code block below. End with a line containing only 'END'.")
        lang = input("Enter language (python, java, bash, batch): ").strip().lower()
        print("Enter your code block:")
        code_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            code_lines.append(line)
        code = '\n'.join(code_lines)
        # Save code to a temp file
        ext_map = {
            'python': '.py',
            'java': '.java',
            'bash': '.sh',
            'batch': '.bat',
            'html': '.html',
            'css': '.css',
        }
        ext = ext_map.get(lang, '.txt')
        temp_file = f'temp_code{ext}'
        with open(temp_file, 'w') as f:
            f.write(code)
        run_code(lang, temp_file)
        os.remove(temp_file)
    print("Running on http://0.0.0.0:5000/")
