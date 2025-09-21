from os import environ
from functools import cache

from aw.config.defaults import CONFIG_DEFAULTS
from aw.config.hardcoded import ENV_KEY_CONFIG, ENV_KEY_SAML

AW_ENV_VARS = {
    'hostnames': ['AW_HOSTNAMES'],
    'port': ['AW_PORT'],
    'proxy': ['AW_PROXY'],
    'address': ['AW_LISTEN', 'AW_LISTEN_ADDRESS'],
    'timezone': ['AW_TIMEZONE'],
    'secret': ['AW_SECRET'],
    'path_run': ['AW_PATH_RUN'],
    'path_play': ['AW_PATH_PLAY', 'ANSIBLE_PLAYBOOK_DIR'],
    'version': ['AW_VERSION'],
    'deployment': ['AW_ENV'],
    'serve_static': ['AW_SERVE_STATIC'],
    'init_admin': ['AW_ADMIN'],
    'init_admin_pwd': ['AW_ADMIN_PWD'],
    'db': ['AW_DB'],
    'db_type': ['AW_DB_TYPE'],
    'db_user': ['AW_DB_USER'],
    'db_pwd': ['AW_DB_PWD'],
    'db_host': ['AW_DB_HOST'],
    'db_socket': ['AW_DB_SOCKET'],
    'db_port': ['AW_DB_PORT'],
    'db_migrate': ['AW_DB_MIGRATE'],
    'run_timeout': ['AW_RUN_TIMEOUT'],
    'path_ansible_config': ['ANSIBLE_CONFIG'],
    'path_log': ['AW_PATH_LOG'],
    'session_timeout': ['AW_SESSION_TIMEOUT'],
    'path_ssh_known_hosts': ['AW_SSH_KNOWN_HOSTS'],
    'ssl_file_crt': ['AW_SSL_CERT'],
    'ssl_file_key': ['AW_SSL_KEY'],
    'debug': ['AW_DEBUG'],
    'audit': ['AW_AUDIT'],
    'auth_mode': ['AW_AUTH'],
    'saml_config': [ENV_KEY_SAML],
}
AW_ENV_VARS_SECRET = ['secret', 'init_admin', 'init_admin_pwd', 'saml_config', 'db_pwd']

AW_ENV_VARS_REV = {}
for key_config, keys_env in AW_ENV_VARS.items():
    for key_env in keys_env:
        AW_ENV_VARS_REV[key_env] = key_config


def get_aw_env_var(var: str) -> (str, None):
    if var in AW_ENV_VARS:
        for key in AW_ENV_VARS[var]:
            if key in environ:
                return environ[key]

    return None


@cache
def get_aw_env_var_or_default(var: str) -> (str, list, None):
    val = get_aw_env_var(var)
    if val is None:
        val = CONFIG_DEFAULTS.get(var, None)

    return val


def check_aw_env_var_is_set(var: str) -> bool:
    return get_aw_env_var(var) is not None


# only use on edge-cases; as.config.main.Config.is_true is preferred
def check_aw_env_var_true(var: str, fallback: bool = False) -> bool:
    val = get_aw_env_var_or_default(var)
    if val is None:
        return fallback

    return str(val).lower() in ['1', 'true', 'y', 'yes']


def auth_mode_saml() -> bool:
    return get_aw_env_var_or_default('auth_mode').lower() == 'saml' and \
        ENV_KEY_SAML in environ and \
        (ENV_KEY_CONFIG in environ and environ[ENV_KEY_CONFIG] != '0')
