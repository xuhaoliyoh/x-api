#!/usr/bin/env python3
"""Disposable API integration test. Never connects to a paid model or production DB.
Creates a uniquely named database and Redis container, then removes both.
A compliance acknowledgement is a SQL fixture in that disposable database only.
"""
import http.server
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
import local

MODEL = 'xapi-smoke-model'
checks = []


def check(label, condition):
    assert condition, label
    checks.append(label)
    print('PASS', label, flush=True)


def docker(*args, input=None):
    return subprocess.run(['docker', *args], env=local.init(), input=input, text=True, capture_output=True, check=True).stdout.strip()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


class Upstream(http.server.BaseHTTPRequestHandler):
    calls = 0
    def log_message(self, *args):
        pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
        if self.path != '/v1/chat/completions':
            self.send_error(404)
            return
        type(self).calls += 1
        self.send_response(200)
        usage = {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        if body.get('stream'):
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            chunks = [
                {'id':'smoke-stream','object':'chat.completion.chunk','created':int(time.time()),'model':MODEL,'choices':[{'index':0,'delta':{'role':'assistant','content':'X-API smoke OK'},'finish_reason':None}]},
                {'id':'smoke-stream','object':'chat.completion.chunk','created':int(time.time()),'model':MODEL,'choices':[{'index':0,'delta':{},'finish_reason':'stop'}],'usage':usage},
            ]
            for chunk in chunks:
                self.wfile.write(('data: '+json.dumps(chunk)+'\n\n').encode())
                self.wfile.flush()
            self.wfile.write(b'data: [DONE]\n\n')
        else:
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'id':'smoke-chat','object':'chat.completion','created':int(time.time()),'model':MODEL,'choices':[{'index':0,'message':{'role':'assistant','content':'X-API smoke OK'},'finish_reason':'stop'}],'usage':usage}).encode())


def main():
    env = local.init()
    suffix = secrets.token_hex(4)
    db = 'xapi_smoke_' + suffix
    redis_name = 'x-api-smoke-' + suffix
    pg = docker('compose', '-f', str(local.ROOT/'dev/compose.yaml'), 'ps', '-q', 'postgres')
    if not pg:
        raise RuntimeError('Start local services with python3 scripts/local.py start first')
    runtime = local.STATE / ('smoke-' + suffix)
    runtime.mkdir(mode=0o700)
    log = (runtime/'server.log').open('wb')
    upstream = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    proc = None
    db_created = redis_created = False
    try:
        docker('exec', pg, 'createdb', '-U', 'xapi', db); db_created = True
        docker('run', '--rm', '-d', '--name', redis_name, '-p', '127.0.0.1::6379', 'redis:8-alpine'); redis_created = True
        redis_port = docker('port', redis_name, '6379/tcp').rsplit(':',1)[1]
        port = free_port()
        base = f'http://127.0.0.1:{port}'
        env.update(DATA_DIR=str(runtime), DATABASE_DBNAME=db, REDIS_PORT=redis_port, REDIS_PASSWORD='', SERVER_PORT=str(port), ADMIN_EMAIL='smoke-admin@example.test', ADMIN_PASSWORD=secrets.token_urlsafe(24), SECURITY_URL_ALLOWLIST_ENABLED='false')
        proc = subprocess.Popen([str(local.STATE/'x-api')], cwd=runtime, env=env, stdout=log, stderr=log)

        def req(path, data=None, token=None, method=None, expected=200):
            headers = {'Content-Type':'application/json','User-Agent':'X-API-local-smoke'}
            if token:
                headers['Authorization']='Bearer '+token
            request = urllib.request.Request(base+path, data=json.dumps(data).encode() if data is not None else None, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=30) as r:
                    status, raw = r.status, r.read().decode()
            except urllib.error.HTTPError as e:
                status, raw = e.code, e.read().decode()
            if status != expected:
                raise AssertionError(f'{path}: expected {expected}, got {status}: {raw[:400]}')
            try:
                parsed=json.loads(raw)
                return parsed.get('data',parsed) if isinstance(parsed,dict) else parsed
            except json.JSONDecodeError:
                return raw

        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError(f'Test server stopped; see {runtime}/server.log')
            try:
                req('/health'); break
            except (OSError, AssertionError):
                time.sleep(1)
        else:
            raise RuntimeError('Startup timeout')
        settings=req('/api/v1/settings/public')
        check('fresh install: X-API, registration enabled, subscription disabled', settings['site_name']=='X-API' and settings['registration_enabled'] and not settings['subscription_enabled'])
        admin=req('/api/v1/auth/login',{'email':env['ADMIN_EMAIL'],'password':env['ADMIN_PASSWORD']})
        at=admin['access_token']
        # SQL fixture in this uniquely named throw-away database, not a real user's consent.
        ack=json.dumps({'version':'v2026.06.10','admin_user_id':admin['user']['id'],'accepted_at':'2026-10-18T00:00:00Z'})
        sql="INSERT INTO settings(key,value) VALUES ('admin_compliance_acknowledgement:%d','%s') ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value;" % (admin['user']['id'],ack)
        docker('exec','-i',pg,'psql','-U','xapi','-d',db,'-v','ON_ERROR_STOP=1',input=sql)
        password=secrets.token_urlsafe(20)
        user=req('/api/v1/auth/register',{'email':'smoke-user@example.test','password':password})
        ut=user['access_token']; uid=user['user']['id']
        check('registration starts with zero balance', user['user']['balance']==0)
        req('/api/v1/auth/register',{'email':'smoke-user@example.test','password':password},expected=409)
        check('duplicate registration rejected',True)
        req('/api/v1/admin/users',token=ut,expected=403)
        for path in ['/api/v1/redeem','/api/v1/payment/orders','/api/v1/user/aff/transfer']:
            req(path,{},ut,expected=403)
        check('ordinary users cannot grant credit or access admin APIs',True)
        check('unconfigured model catalog is empty',req('/api/v1/x-api/models',token=ut)==[])
        group=req('/api/v1/admin/groups',{'name':'Smoke model group','platform':'openai','subscription_type':'standard','rate_multiplier':1,'model_pricing':[{'platform':'openai','models':[MODEL],'billing_mode':'token','input_price':0.000001,'output_price':0.000002}]},at)
        gid=group['id']
        account=req('/api/v1/admin/accounts',{'name':'Disposable mock upstream','platform':'openai','type':'apikey','credentials':{'api_key':'mock-test-only','base_url':f'http://127.0.0.1:{upstream.server_port}','model_mapping':{MODEL:MODEL}},'extra':{'openai_responses_mode':'force_chat_completions'},'group_ids':[gid],'concurrency':2,'priority':1,'rate_multiplier':1},at)
        key=req('/api/v1/keys',{'name':'smoke-key','group_id':gid},ut)
        kt=key['key']; kid=key['id']
        chat={'model':MODEL,'messages':[{'role':'user','content':'hello'}],'stream':False}
        req('/v1/chat/completions',chat,kt,expected=403)
        check('zero balance blocks model requests before upstream',Upstream.calls==0)
        req(f'/api/v1/admin/users/{uid}/balance',{'balance':1,'operation':'add','notes':'Disposable smoke test allocation'},at)
        check('admin quota allocation persists',req('/api/v1/user/profile',token=ut)['balance']==1)
        models=req('/v1/models',token=kt)
        # req unwraps the OpenAI data array.
        check('API model catalog contains only configured IDs',[m['id'] for m in models]==[MODEL])
        check('client-version query cannot expose a provider default catalog', [m['id'] for m in req('/v1/models?client_version=smoke',token=kt)]==[MODEL])
        check('single-model endpoint matches the catalog',req('/v1/models/'+MODEL,token=kt)['id']==MODEL)
        req('/v1/models/not-configured',token=kt,expected=404)
        req('/v1/chat/completions',{**chat,'model':'gpt-not-configured'},kt,expected=400)
        check('unknown models rejected before upstream',Upstream.calls==0)
        response=req('/v1/chat/completions',chat,kt)
        check('non-streaming completion forwarded',response['choices'][0]['message']['content']=='X-API smoke OK')
        stream=req('/v1/chat/completions',{**chat,'stream':True,'stream_options':{'include_usage':True}},kt)
        check('streaming completion and terminal event forwarded','X-API smoke OK' in stream and '[DONE]' in stream)
        for _ in range(30):
            profile=req('/api/v1/user/profile',token=ut)
            if profile['balance']<1: break
            time.sleep(0.5)
        check('successful calls deduct balance',0<profile['balance']<1)
        usage=req('/api/v1/usage',token=ut)
        check('usage records include the actual model',any(x.get('model')==MODEL for x in usage.get('items',[])))
        other=req('/api/v1/auth/register',{'email':'smoke-other@example.test','password':password})
        req(f'/api/v1/keys/{kid}',token=other['access_token'],expected=404)
        check('users cannot read another users key',True)
        req(f'/api/v1/keys/{kid}',{'status':'inactive'},ut,method='PUT')
        req('/v1/chat/completions',chat,kt,expected=401)
        check('disabled key can no longer call upstream',True)
        new_password=secrets.token_urlsafe(20)
        req('/api/v1/user/password',{'old_password':password,'new_password':new_password},ut,method='PUT')
        req('/api/v1/auth/login',{'email':'smoke-user@example.test','password':password},expected=401)
        req('/api/v1/auth/login',{'email':'smoke-user@example.test','password':new_password})
        check('password change invalidates old password',True)
        req(f"/api/v1/admin/accounts/{account['id']}",{'status':'inactive','schedulable':False},at,method='PUT')
        check('disabled upstream disappears from the user model catalog',req('/api/v1/x-api/models',token=other['access_token'])==[])
        (local.STATE/'smoke-report.json').write_text(json.dumps({'checks':checks,'upstream':'local deterministic mock; no external inference','passed':True},ensure_ascii=False,indent=2)+'\n')
        print(f'{len(checks)} integration checks passed; disposable resources will be removed.',flush=True)
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=30)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        log.close(); upstream.shutdown()
        if db_created: docker('exec',pg,'dropdb','-U','xapi','--force',db)
        if redis_created: docker('rm','-f',redis_name)


if __name__=='__main__':
    main()
