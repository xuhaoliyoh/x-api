#!/usr/bin/env python3
"""Local X-API lifecycle. Credentials and runtime state stay in .local/."""
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / '.local'
ENV_FILE = STATE / 'environment.json'
URL = 'http://127.0.0.1:18080'


def init():
    STATE.mkdir(mode=0o700, exist_ok=True)
    if not ENV_FILE.exists():
        env = dict(AUTO_SETUP='true', DATA_DIR=str(STATE / 'data'),
                   SERVER_HOST='127.0.0.1', SERVER_PORT='18080', SERVER_MODE='release',
                   DATABASE_HOST='127.0.0.1', DATABASE_PORT='25432', DATABASE_USER='xapi',
                   DATABASE_DBNAME='xapi', DATABASE_PASSWORD=secrets.token_hex(24),
                   DATABASE_SSLMODE='disable', REDIS_HOST='127.0.0.1', REDIS_PORT='26379',
                   REDIS_PASSWORD=secrets.token_hex(24), JWT_SECRET=secrets.token_hex(32),
                   ADMIN_EMAIL='admin@x-api.local', ADMIN_PASSWORD=secrets.token_urlsafe(24),
                   DEFAULT_USER_BALANCE='0', TZ='Asia/Shanghai')
        ENV_FILE.write_text(json.dumps(env, indent=2) + '\n')
        ENV_FILE.chmod(0o600)
        (STATE / 'data').mkdir(mode=0o700, exist_ok=True)
    return {**os.environ, **json.loads(ENV_FILE.read_text())}


def run(args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, env=init(), check=True)


def compose(*args):
    run(['docker', 'compose', '-f', str(ROOT / 'dev/compose.yaml'), *args])


def build():
    run(['pnpm', 'install', '--frozen-lockfile'], ROOT / 'frontend')
    run(['pnpm', 'build'], ROOT / 'frontend')
    run(['go', 'build', '-tags', 'embed', '-trimpath', '-ldflags=-X main.Version=0.1.0-xapi',
         '-o', str(STATE / 'x-api'), './cmd/server'], ROOT / 'backend')


def running():
    pidfile = STATE / 'server.pid'
    if not pidfile.exists():
        return None
    pid = int(pidfile.read_text())
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True)
    return pid if str(STATE / 'x-api') in result.stdout else None


def start():
    compose('up', '-d', '--wait', '--wait-timeout', '120')
    if running():
        print(f'X-API already running: {URL}')
        return
    if not (STATE / 'x-api').exists():
        build()
    with (STATE / 'server.log').open('ab') as log:
        proc = subprocess.Popen([str(STATE / 'x-api')], cwd=STATE, env=init(),
                                stdout=log, stderr=log, start_new_session=True)
    (STATE / 'server.pid').write_text(str(proc.pid))
    for _ in range(120):
        if proc.poll() is not None:
            raise RuntimeError(f'Startup failed; inspect {STATE / "server.log"}')
        try:
            with urllib.request.urlopen(URL + '/health', timeout=2) as response:
                if response.status == 200:
                    print(f'X-API ready: {URL}\nAdmin credentials: {ENV_FILE}')
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(1)
    raise RuntimeError(f'Health check timed out; inspect {STATE / "server.log"}')


def stop_server():
    pid = running()
    if pid:
        os.kill(pid, signal.SIGTERM)
        for _ in range(30):
            if not running():
                break
            time.sleep(1)
        if running():
            raise RuntimeError('Server is still shutting down; try again shortly.')
    (STATE / 'server.pid').unlink(missing_ok=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd not in {'init', 'build', 'start', 'stop', 'restart', 'status'}:
        raise SystemExit('Usage: python3 scripts/local.py {init|build|start|stop|restart|status}')
    init()
    if cmd == 'init':
        print(f'Local configuration ready: {ENV_FILE}')
    elif cmd == 'build':
        build()
    elif cmd == 'start':
        start()
    elif cmd == 'stop':
        stop_server()
        compose('stop')
    elif cmd == 'restart':
        stop_server()
        start()
    else:
        print(f'X-API: {"running" if running() else "stopped"} — {URL}')
        compose('ps')


if __name__ == '__main__':
    main()
