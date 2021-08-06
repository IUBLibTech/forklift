import sys
import subprocess
import urllib.request
from bottle import Bottle, request, abort, run
from json import dumps
from ast import literal_eval

sys.version_info.major >= 3 or sys.exit('ERROR: Python 3 required')
app = Bottle()
app.config.load_config('./forklift.config')


@app.get('/status')
def status():
    return 'OK'


@app.post('/hook')
def hook():
    request.params.apikey == app.config['forklift.api_key'] or abort(403, 'Forbidden')
    print("Request params: {}".format(dumps(request.params.dict)))
    params = request.json or abort(400, 'Params not found')
    repo_name = params['repository']['repo_name']
    container = validate_container(repo_name)
    container or abort(404, "Valid container {}:{} not found".format(repo_name, container))
    validate_tag(params['push_data']['tag'], container) or abort(304, 'Not modified')

    # All checks passed, go for restart.
    # Callback may timeout if it waits for the container to restart, so call now.
    validate_webhook(params.get('callback_url'), 'success')
    try:
        output = restart(container['target'])
    except subprocess.CalledProcessError as e:
        abort(500, 'Restart failed: {} {}'.format(e.returncode, e.output))
    return "OK\n{}".format(output)


def validate_container(key):
    try:
        return literal_eval(app.config['forklift.valid_containers'])[key]
    except KeyError:
        return False


def validate_tag(tag, container):
    return tag == container['tag']


def validate_webhook(url, state):
    if url is None:
        return
    data = dumps({'state': state}).encode()
    req = urllib.request.Request(url=url, data=data, method='POST')
    print("Validating webhook: {} => {}".format(state, url))
    return urllib.request.urlopen(req)


def restart(target):
    cmd = "{}/{}".format(app.config['forklift.docker_root'], target)
    print("Running command: {}".format(cmd))
    return subprocess.check_output(cmd)
    # return os.spawnl(os.P_NOWAIT, cmd)


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=app.config['forklift.port'], debug=False, reloader=False)
