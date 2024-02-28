import bottle
import sys
import subprocess
import logging
import re
import urllib.request
from bottle import get, post, request, abort, run
from json import dumps
from ast import literal_eval

sys.version_info.major >= 3 or sys.exit('ERROR: Python 3 required')
app = bottle.default_app()
app.config.load_config('./forklift.config')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


@get('/status')
def status():
    return 'OK'


@post('/hook')
def hook():
    request.params.apikey == app.config['forklift.api_key'] or abort(403, 'Forbidden')
    logging.debug("Request params: {}".format(dumps(request.params.dict)))
    params = request.json or abort(400, 'Params not found')

    # Get data from webhook data
    tag = params['push_data']['tag']
    repo_name = params['repository']['repo_name']

    # Verify a configuration exists for this repo_name and tag combo
    container = validate_container(repo_name, tag)
    container or abort(404, "Valid container {}/{}:{} not found".format(repo_name, container, tag))

    # Send a callback request
    # validate_webhook(params.get('callback_url'), 'success')

    # Exec the restart command
    output = restart(container) or abort(500, 'Restart failed')
    return "OK\n{}".format(output)

@post('/gh_hook')
def gh_hook():
    request.params.apikey == app.config['forklift.api_key'] or abort(403, 'Forbidden')
    logging.debug("Request params: {}".format(dumps(request.params.dict)))
    params = request.json or abort(400, 'Params not found')
    event = request.get_header('X-GitHub-Event')

    # Get data from webhook data
    tag = params['ref']
    repo_name = params['repository']['full_name']

    # Verify a configuration exists for this repo_name and tag combo
    container = validate_container(repo_name, tag)
    container or abort(404, "Valid container {}/{}:{} not found".format(repo_name, container, tag))

    # Exec the restart command
    if event == 'push':
        output = restart(container) or abort(500, 'Restart failed')
        return "{} event: OK\n{}".format(event, output)


def validate_container(repo_name, tag):
    try:
        container = literal_eval(app.config['forklift.valid_containers'])[repo_name]
        target = [t['target'] for t in container if re.compile(t['tag']).fullmatch(tag)][0]
    except (IndexError, KeyError):
        logging.warning("Invalid container {}:{}".format(repo_name, tag))
        return False
    else:
        return target


def validate_webhook(url, state):
    if url is None:
        return
    data = dumps({'state': state}).encode()
    req = urllib.request.Request(url=url, data=data, method='POST')
    logging.debug("Validating webhook: {} => {}".format(state, url))
    try:
        callback_resp = urllib.request.urlopen(req)
    except urllib.URLError as e:
        logging.warning("Callback webhook ({}) failed: {}".format(url, e.reason))
    finally:
        return callback_resp


def restart(container_name):
    logging.info("Restarting {}".format(container_name))
    cmd = "{}/{}".format(app.config['forklift.docker_root'], container_name)
    logging.debug("Running command: {}".format(cmd))
    return subprocess.check_output(cmd)
    # return os.spawnl(os.P_NOWAIT, cmd)


if __name__ == '__main__':
    run(host='0.0.0.0', port=app.config['forklift.port'], debug=False, reloader=False)
