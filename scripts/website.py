"""Build or preview the Sphinx website with one command from any directory."""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def website_python():
    local = ROOT / '.venv' / 'website' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if local.is_file():
        return str(local)
    if importlib.util.find_spec('sphinx'):
        return sys.executable
    raise ValueError('Website dependencies are missing. Run: python3 -m pip install -r website/requirements.txt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'preview', 'publish'))
    parser.add_argument('task', nargs='?', type=Path, help='Reviewed task folder for publish')
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if (args.command == 'publish') != (args.task is not None):
        parser.error('publish requires a task folder; build and preview do not take a task')
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    try:
        python = website_python()
        output = args.output.resolve()
        if args.command == 'publish':
            subprocess.run([python, str(ROOT / 'scripts/visualization_workflow.py'), 'publish',
                            str(args.task.resolve())], cwd=ROOT, check=True)
        subprocess.run([python, '-m', 'sphinx', '-b', 'dirhtml', '-W', '--keep-going', '-n',
                        str(ROOT / 'website'), str(output)], cwd=ROOT, check=True)
        if args.command == 'preview':
            print(f'Preview: http://localhost:{args.port}/ (Ctrl+C to stop; rebuild after edits)', flush=True)
            subprocess.run([python, '-m', 'http.server', str(args.port), '--bind', '127.0.0.1',
                            '--directory', str(output)], cwd=ROOT, check=True)
    except KeyboardInterrupt:
        return
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'website: {error}\n')


if __name__ == '__main__':
    main()
