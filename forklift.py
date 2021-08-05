import bottle
import sys, os, subprocess, urllib.request
from bottle import get, post, request, abort, run
from json import dumps
from ast import literal_eval

sys.version_info.major >= 3 or sys.exit('ERROR: Python 3 required')
app = bottle.default_app()
app.config.load_config('./forklift.config')

@get('/status')
def status():
    return 'OK'

@post('/hook')
def hook():
    request.params.apikey == app.config['forklift.api_key'] or abort(403, 'Forbidden')
    print("Request params: {}".format(dumps(request.params.dict)))
    params = request.json or abort(400, 'Params not found')
    params['push_data']['tag'] == 'master' or abort(304, 'Not modified')
    repo_name = params['repository']['repo_name']
    container = validate_container(repo_name)
    container or abort(404, "Valid container {}:{} not found".format(repo_name, container))
    validate_webhook(params.get('callback_url'), 'success')
    output = restart(container) or abort(500, 'Restart failed')
    return "OK\n{}".format(output)

def validate_container(key):
    return literal_eval(app.config['forklift.valid_containers'])[key]

def validate_webhook(url, state):
    if url == None: return
    data = dumps({'state':state}).encode()
    req = urllib.request.Request(url=url, data=data, method='POST')
    print("Validating webhook: {} => {}".format(state, url))
    return urllib.request.urlopen(req)

def restart(container_name):
    cmd = "{}/{}/bin/update".format(app.config['forklift.docker_root'], container_name)
    print("Running command: {}".format(cmd))
    return subprocess.check_output(cmd)
    # return os.spawnl(os.P_NOWAIT, cmd)

run(host='0.0.0.0', port=app.config['forklift.port'], debug=False, reloader=False)
