from bottle import get, post, request, abort, run
import os

# Must get provided in request (i.e. /hook?apikey=12345678)
apikey = '1234'
# Absolute path to docker containers
docker_root = '/srv/docker'
# Map of Docker Hub repo names and directory names
valid_containers = {'namespace/name':'docker_dir'}

@get('/status')
def status():
    return 'OK'

@post('/hook')
def hook():
    request.params.apikey == apikey or abort(403, 'Forbidden')
    params = request.json or abort(400, 'Params not found')
    params['push_data']['tag'] == 'master' or abort(304, 'Not modified')
    container = valid_containers[params['repository']['repo_name']] or abort(404, 'Valid container not found')
    restart(container) or abort(500, 'Restart failed')
    return 'OK'

def restart(container_name):
    cmd = "{}/{}/restart".format(docker_root, container_name)
    return os.spawnl(os.P_NOWAIT, cmd)

run(host='0.0.0.0', port=8000, debug=False, reloader=False)
