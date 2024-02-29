from webtest import TestApp as WebTestApp
import forklift
import subprocess

forklift_app = forklift.app
forklift_app.config.load_config('./example.config')
app = WebTestApp(forklift_app)


def test_status_ok():
    assert app.get('/status').status == '200 OK'


def test_hook_no_apikey():
    assert app.post_json('/hook', expect_errors=True).status == '403 Forbidden'


def test_hook_bad_apikey():
    assert app.post_json('/hook?apikey=badkey', expect_errors=True).status == '403 Forbidden'


def test_hook_no_json():
    assert app.post_json('/hook?apikey=12345', expect_errors=True).status == '400 Bad Request'


def test_hook_tag_mismatch():
    data = {'push_data': {'tag': 'badtag'}, 'repository': {'repo_name': 'docker_user/image_name'}}
    assert app.post_json('/hook?apikey=12345', data, expect_errors=True).status == '404 Not Found'


def test_hook_invalid_container():
    data = {'push_data': {'tag': 'latest'}, 'repository': {'repo_name': 'bad_docker_user/image_name'}}
    assert app.post_json('/hook?apikey=12345', data, expect_errors=True).status == '404 Not Found'


def test_hook_restart_failed(mocker):
    mocker.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError)
    data = {'push_data': {'tag': 'latest'}, 'repository': {'repo_name': 'docker_user/image_name'}}
    assert app.post_json('/hook?apikey=12345', data, expect_errors=True).status == '500 Internal Server Error'
    subprocess.check_output.assert_called_once_with('/srv/docker/target_dir/update')


def test_hook_success(mocker):
    mocker.patch('subprocess.check_output', return_value="Mocked subprocess call success")
    data = {'push_data': {'tag': 'latest'}, 'repository': {'repo_name': 'docker_user/image_name'}}
    assert app.post_json('/hook?apikey=12345', data).status == '200 OK'
    subprocess.check_output.assert_called_once_with('/srv/docker/target_dir/update')

def test_gh_hook_success(mocker):
    mocker.patch('subprocess.check_output', return_value="Mocked subprocess call success")
    data = {'ref': 'refs/heads/main', 'repository': {'full_name': 'gh_user/repo_name'}}
    assert app.post_json('/gh_hook?apikey=12345', data, headers={'X-GitHub-Event': 'push'}).status == '200 OK'
    subprocess.check_output.assert_called_once_with('/srv/docker/target_dir/update')

def test_hook_success_alt_tag(mocker):
    mocker.patch('subprocess.check_output', return_value="Mocked subprocess call success")
    data = {'push_data': {'tag': 'main'}, 'repository': {'repo_name': 'docker_user/image_name'}}
    assert app.post_json('/hook?apikey=12345', data).status == '200 OK'
    subprocess.check_output.assert_called_once_with('/srv/docker/target_dir/update')

def test_hook_success_other_regexp(mocker):
    mocker.patch('subprocess.check_output', return_value="Mocked subprocess call success")
    data = {'push_data': {'tag': 'stable-0.1-rc1'}, 'repository': {'repo_name': 'other_user/other_name'}}
    assert app.post_json('/hook?apikey=12345', data).status == '200 OK'
    subprocess.check_output.assert_called_once_with('/srv/docker/other_target_dir/update')


def test_validate_container():
    assert not forklift.validate_container('bad_docker_user/image_name', 'latest')
    assert forklift.validate_container('docker_user/image_name', 'latest') == 'target_dir/update'
