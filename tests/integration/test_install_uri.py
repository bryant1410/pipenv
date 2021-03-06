import pytest

from flaky import flaky


@pytest.mark.vcs
@pytest.mark.install
@pytest.mark.needs_internet
@flaky
def test_basic_vcs_install(PipenvInstance, pip_src_dir, pypi):
    with PipenvInstance(pypi=pypi, chdir=True) as p:
        c = p.pipenv('install git+https://github.com/benjaminp/six.git#egg=six')
        assert c.return_code == 0
        # edge case where normal package starts with VCS name shouldn't be flagged as vcs
        c = p.pipenv('install gitdb2')
        assert c.return_code == 0
        assert all(package in p.pipfile['packages'] for package in ['six', 'gitdb2'])
        assert 'git' in p.pipfile['packages']['six']
        assert p.lockfile['default']['six'] == {"git": "https://github.com/benjaminp/six.git"}
        assert 'gitdb2' in p.lockfile['default']


@pytest.mark.files
@pytest.mark.urls
@pytest.mark.needs_internet
@flaky
def test_urls_work(PipenvInstance, pypi, pip_src_dir):
    with PipenvInstance(pypi=pypi) as p:
        c = p.pipenv('install https://github.com/divio/django-cms/archive/release/3.4.x.zip')
        assert c.return_code == 0

        dep = list(p.pipfile['packages'].values())[0]
        assert 'file' in dep, p.pipfile

        dep = list(p.lockfile['default'].values())[0]
        assert 'file' in dep, p.lockfile


@pytest.mark.files
@pytest.mark.urls
@pytest.mark.needs_internet
@flaky
def test_install_remote_requirements(PipenvInstance, pypi):
    with PipenvInstance(pypi=pypi) as p:
        # using a github hosted requirements.txt file
        c = p.pipenv('install -r https://raw.githubusercontent.com/kennethreitz/pipenv/3688148ac7cfecefb085c474b092c31d791952c1/tests/test_artifacts/requirements.txt')

        assert c.return_code == 0
        # check Pipfile with versions
        assert 'requests' in p.pipfile['packages']
        assert p.pipfile['packages']['requests'] == u'==2.18.4'
        assert 'records' in p.pipfile['packages']
        assert p.pipfile['packages']['records'] == u'==0.5.2'

        # check Pipfile.lock
        assert 'requests' in p.lockfile['default']
        assert 'records' in p.lockfile['default']


@pytest.mark.e
@pytest.mark.vcs
@pytest.mark.install
@pytest.mark.needs_internet
@flaky
def test_editable_vcs_install(PipenvInstance, pip_src_dir, pypi):
    with PipenvInstance(pypi=pypi) as p:
        c = p.pipenv('install -e git+https://github.com/requests/requests.git#egg=requests')
        assert c.return_code == 0
        assert 'requests' in p.pipfile['packages']
        assert 'git' in p.pipfile['packages']['requests']
        assert 'editable' in p.pipfile['packages']['requests']
        assert 'editable' in p.lockfile['default']['requests']
        assert 'chardet' in p.lockfile['default']
        assert 'idna' in p.lockfile['default']
        assert 'urllib3' in p.lockfile['default']
        assert 'certifi' in p.lockfile['default']


@pytest.mark.install
@pytest.mark.vcs
@pytest.mark.tablib
@pytest.mark.needs_internet
@flaky
def test_install_editable_git_tag(PipenvInstance, pip_src_dir):
    # This uses the real PyPI since we need Internet to access the Git
    # dependency anyway.
    with PipenvInstance() as p:
        c = p.pipenv('install -e git+https://github.com/benjaminp/six.git@1.11.0#egg=six')
        assert c.return_code == 0
        assert 'six' in p.pipfile['packages']
        assert 'six' in p.lockfile['default']
        assert 'git' in p.lockfile['default']['six']
        assert p.lockfile['default']['six']['git'] == 'https://github.com/benjaminp/six.git'
        assert 'ref' in p.lockfile['default']['six']
