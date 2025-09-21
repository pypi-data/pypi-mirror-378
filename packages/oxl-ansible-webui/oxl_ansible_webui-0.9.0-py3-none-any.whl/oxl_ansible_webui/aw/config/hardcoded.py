# todo: some of these settings could be moved to the system-config later on

THREAD_JOIN_TIMEOUT = 3
INTERVAL_RELOAD = 10  # start/stop threads for configured jobs
INTERVAL_CHECK = 5  # check for queued jobs
LOGIN_PATH = '/a/login/'
LOGOUT_PATH = '/o/'
LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'
SHORT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FILE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
KEY_TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
MIN_SECRET_LEN = 30
JOB_EXECUTION_LIMIT = 20
GRP_MANAGER = {
    'full': 'AW Managers',
    'job': 'AW Job Managers',
    'exec': 'AW Job Executors',
    'permission': 'AW Permission Managers',
    'repository': 'AW Repository Managers',
    'credentials': 'AW Credentials Managers',
    'alert': 'AW Alert Managers',
    'system': 'AW System Managers',
}
REPO_CLONE_TIMEOUT = 300
ENV_KEY_CONFIG = 'AW_CONFIG'
ENV_KEY_SAML = 'AW_SAML'
SECRET_HIDDEN = '⬤' * 15
