"""Build or preview the Sphinx website with one command from any directory."""

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def website_python():
    local = ROOT / '.venv' / 'website' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if local.is_file():
        return str(local)
    if importlib.util.find_spec('sphinx'):
        return sys.executable
    raise ValueError('Website dependencies are missing. Run: python3 -m pip install -r website/requirements.txt')


def build(python, output):
    # Build from scratch so renamed/deleted posts and assets cannot linger.
    # Keep the last working preview if Sphinx rejects the new content.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.website-build-', dir=output.parent) as directory:
        staged = Path(directory) / 'html'
        subprocess.run([python, '-m', 'sphinx', '-b', 'dirhtml', '-W', '--keep-going', '-n',
                        str(ROOT / 'website'), str(staged)], cwd=ROOT, check=True)
        if output.exists():
            shutil.rmtree(output)
        staged.rename(output)


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
        if args.output.is_symlink():
            raise ValueError('The output directory must not be a symlink.')
        output = args.output.resolve()
        if ROOT.is_relative_to(output) or output.is_relative_to(ROOT / 'website'):
            raise ValueError('The output directory must be separate from the website source and repository root.')
        if output.exists() and (not output.is_dir() or
                                (any(output.iterdir()) and not (output / '.nojekyll').is_file())):
            raise ValueError('Refusing to replace a nonempty directory without a generated .nojekyll marker.')
        python = website_python()
        if args.command == 'publish':
            subprocess.run([python, str(ROOT / 'scripts/visualization_workflow.py'), 'publish',
                            str(args.task.resolve())], cwd=ROOT, check=True)
        build(python, output)
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
