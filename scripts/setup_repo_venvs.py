from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
VENVS_DIR = ROOT / 'data' / 'venvs'
REPO_DEPS: dict[str,
                list[str]] = {'requests': ['pytest>=7,<9',
                                           'pytest-httpbin>=2.0.0',
                                           'pytest-mock',
                                           'trustme',
                                           'charset_normalizer>=2,<4',
                                           'idna>=2.5,<4',
                                           'urllib3>=1.21.1,<3',
                                           'certifi>=2017.4.17'],
                              'flask': ['pytest>=7,<8',
                                        'Werkzeug>=2.0,<3',
                                        'Jinja2>=3.0,<4',
                                        'itsdangerous>=2.0,<3',
                                        'click>=8.0,<9',
                                        'blinker',
                                        'asgiref>=3.2',
                                        'python-dotenv',
                                        'greenlet'],
                              'httpie': ['pytest>=7,<8',
                                         'pytest-httpbin>=2.0.0',
                                         'pytest-mock',
                                         'requests>=2.22.0',
                                         'Pygments>=2.5.2',
                                         'requests-toolbelt>=0.9.1',
                                         'PySocks',
                                         'colorama>=0.2.4',
                                         'responses',
                                         'multidict',
                                         'charset_normalizer',
                                         'defusedxml',
                                         'werkzeug<3']}
PYTHONPATH_LAYOUT: dict[str, str] = {'requests': 'src', 'flask': 'src', 'httpie': ''}


def venv_python(repo: str) -> Path:
    if os.name == 'nt':
        return VENVS_DIR / repo / 'Scripts' / 'python.exe'
    return VENVS_DIR / repo / 'bin' / 'python'


def venv_ready(repo: str) -> bool:
    return (VENVS_DIR / repo / 'READY').is_file()


def create_venv(repo: str) -> None:
    target = VENVS_DIR / repo
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_dir():
        print(f'[setup] creating venv {target}')
        subprocess.run([sys.executable, '-m', 'venv', str(target)], check=True)
    py = venv_python(repo)
    print(f'[setup] upgrading pip in {repo} venv')
    subprocess.run([str(py), '-m', 'pip', 'install', '--upgrade',
                   'pip', 'setuptools', 'wheel'], check=True)
    deps = REPO_DEPS[repo]
    print(f'[setup] installing {len(deps)} deps for {repo}')
    subprocess.run([str(py), '-m', 'pip', 'install', *deps], check=True)
    (target / 'READY').write_text(json.dumps({'repo': repo,
                                              'deps': deps}, indent=2), encoding='utf-8')
    print(f'[setup] {repo} ready: {py}')


def write_manifest() -> None:
    manifest = {
        repo: {
            'python': str(
                venv_python(repo)),
            'pythonpath_layout': PYTHONPATH_LAYOUT[repo],
            'ready': venv_ready(repo)} for repo in REPO_DEPS}
    out = VENVS_DIR / 'manifest.json'
    out.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'[setup] manifest written: {out}')


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--repos', nargs='*', default=list(REPO_DEPS.keys()))
    p.add_argument('--force', action='store_true', help='reinstall even if READY marker exists')
    args = p.parse_args()
    for repo in args.repos:
        if repo not in REPO_DEPS:
            print(f'[setup] unknown repo: {repo}', file=sys.stderr)
            continue
        if venv_ready(repo) and (not args.force):
            print(f'[setup] {repo}: READY (skipping)')
            continue
        create_venv(repo)
    write_manifest()


if __name__ == '__main__':
    main()
