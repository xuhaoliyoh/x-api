#!/usr/bin/env python3
"""Build a Linux/amd64 release on the workstation; never use upstream binaries."""
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '.local' / 'deploy'
CONTEXT = OUT / 'context'


def run(args, cwd=ROOT, **kwargs):
    subprocess.run(args, cwd=cwd, check=True, **kwargs)


def main():
    OUT.mkdir(parents=True, exist_ok=True, mode=0o700)
    CONTEXT.mkdir(exist_ok=True)
    commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip()
    image = f'x-api:{commit}'
    run(['pnpm', 'install', '--frozen-lockfile'], ROOT / 'frontend')
    run(['pnpm', 'build'], ROOT / 'frontend')
    env = {**os.environ, 'CGO_ENABLED': '0', 'GOOS': 'linux', 'GOARCH': 'amd64'}
    run(['go', 'build', '-tags', 'embed', '-trimpath',
         f'-ldflags=-s -w -X main.Version=0.1.0-xapi -X main.Commit={commit} -X main.BuildType=release',
         '-o', str(CONTEXT / 'x-api'), './cmd/server'], ROOT / 'backend', env=env)
    shutil.copytree(ROOT / 'backend/resources', CONTEXT / 'resources', dirs_exist_ok=True)
    for name in ('LICENSE', 'COPYING', 'UPSTREAM.md'):
        shutil.copy2(ROOT / name, CONTEXT / name)
    for base in ('postgres:18-alpine', 'redis:8-alpine'):
        run(['docker', 'pull', '--platform', 'linux/amd64', base])
    run(['docker', 'build', '--platform', 'linux/amd64', '-f',
         str(ROOT / 'deploy/x-api/Dockerfile.runtime'), '-t', image, str(CONTEXT)])
    (OUT / 'image.txt').write_text(image + '\n')
    # --platform excludes any ARM layers cached by local development.
    run(['docker', 'image', 'save', '--platform', 'linux/amd64', '-o', str(OUT / 'images.tar'),
         image, 'postgres:18-alpine', 'redis:8-alpine'])
    run(['gzip', '-f', str(OUT / 'images.tar')])
    print(f'Release: {image}\nBundle: {OUT / "images.tar.gz"}')


if __name__ == '__main__':
    main()
