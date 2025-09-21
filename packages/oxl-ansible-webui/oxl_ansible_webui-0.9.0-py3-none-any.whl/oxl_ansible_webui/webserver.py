from pathlib import Path
from multiprocessing import cpu_count
from ssl import SSLContext, TLSVersion
from ssl import CERT_NONE as VERIFY_CERT_NONE

import gunicorn
from gunicorn.app.wsgiapp import WSGIApplication

from aw.utils.deployment import deployment_dev, deployment_docker
from aw.utils.debug import log, warn_if_development
from aw.config.environment import get_aw_env_var_or_default, get_aw_env_var

TLSv1_2 = TLSVersion(771)
PORT_WEB = get_aw_env_var_or_default('port')
LISTEN_ADDRESS = get_aw_env_var_or_default('address')

# https://docs.gunicorn.org/en/stable/settings.html
OPTIONS_DEV = {
    'reload': True,
    'loglevel': 'info',
    'workers': 2,
}
OPTIONS_PROD = {
    'bind': f'{LISTEN_ADDRESS}:{PORT_WEB}',
    'reload': False,
    'loglevel': 'warning',
}

if deployment_docker():
    OPTIONS_PROD['bind'] = f'0.0.0.0:{PORT_WEB}'


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


def ssl_context(conf, default_ssl_context_factory) -> SSLContext:
    del conf
    ctx = default_ssl_context_factory()
    ctx.minimum_version = TLSv1_2
    ctx.verify_mode = VERIFY_CERT_NONE
    return ctx


def init_webserver():
    gunicorn.SERVER = 'Ansible WebUI'
    opts = {
        'workers': (cpu_count() * 2) + 1,
        **OPTIONS_PROD
    }
    if deployment_dev():
        warn_if_development()
        opts = {**opts, **OPTIONS_DEV}

    scheme = 'http'
    ssl_cert = get_aw_env_var('ssl_file_crt')
    ssl_key = get_aw_env_var('ssl_file_key')
    if ssl_cert is not None and ssl_key is not None:
        if not Path(ssl_cert).is_file() or not Path(ssl_key).is_file():
            log(
                msg=f"Either SSL certificate or SSL key is not readable: {ssl_cert}, {ssl_key}",
                level=1,
            )

        else:
            opts = {
                **opts,
                'keyfile': ssl_key,
                'certfile': ssl_cert,
                'ssl_context': ssl_context,
                'do_handshake_on_connect': True,
            }
            scheme = 'https'

    log(msg=f"Listening on {scheme}://{opts['bind']}", level=5)

    StandaloneApplication(
        app_uri="aw.main:app",
        options=opts
    ).run()
