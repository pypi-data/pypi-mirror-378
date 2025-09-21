import unicodedata
import re as regex
from platform import python_version
from datetime import datetime, timedelta
from time import time
from os import open as open_file
from os import remove as remove_file
from pathlib import Path
from functools import lru_cache, wraps
from math import ceil
from sys import maxunicode
from random import choice as random_choice
from string import digits, ascii_letters, punctuation
from importlib.metadata import distribution as get_distribution

from pytz import utc
from crontab import CronTab
from django.utils.html import escape as escape_html

from aw.config.main import config
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.utils.util_no_config import set_timezone
from aw.config.defaults import behind_proxy, inside_docker

# allow import from other modules
# pylint: disable=W0611
from aw.utils.util_no_config import is_set, is_null


def datetime_w_tz() -> datetime:
    return datetime.now(config.timezone)


def datetime_from_db(dt: (datetime, None)) -> (datetime, None):
    # datetime form db will always be UTC; convert it
    if not isinstance(dt, datetime):
        return None

    local_dt = dt.replace(tzinfo=utc).astimezone(config.timezone)
    return config.timezone.normalize(local_dt)


def datetime_from_db_str(dt: (datetime, None), fmt: str = SHORT_TIME_FORMAT) -> str:
    dt = datetime_from_db(dt)
    if not isinstance(dt, datetime):
        return ''

    return dt.strftime(fmt)


def get_next_cron_execution_sec(schedule: str) -> float:
    try:
        cron = CronTab(schedule)
        set_timezone(str(config.timezone))
        return cron.next(now=datetime_w_tz())

    except ValueError:
        return -1


def get_next_cron_execution(schedule: str, wait_sec: (int, float) = None) -> (datetime, None):
    if wait_sec is None:
        wait_sec = get_next_cron_execution_sec(schedule)
        if wait_sec == -1:
            return None

    return datetime.fromtimestamp(time() + wait_sec)


def get_next_cron_execution_str(schedule: str, wait_sec: (int, float) = None) -> str:
    next_exec_dt = get_next_cron_execution(schedule, wait_sec)
    if next_exec_dt is None:
        return ''

    return next_exec_dt.strftime(SHORT_TIME_FORMAT)


def _open_file_0600(path: (str, Path), flags):
    return open_file(path, flags, 0o600)


def write_file_0600(file: (str, Path), content: str):
    mode = 'w'
    if Path(file).is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0600) as _file:
        _file.write(content)


def _open_file_0640(path: (str, Path), flags):
    return open_file(path, flags, 0o640)


def write_file_0640(file: (str, Path), content: str):
    mode = 'w'
    if Path(file).is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0640) as _file:
        _file.write(content)


def get_random_str(l: int = 50) -> str:
    return ''.join(random_choice(ascii_letters + digits + punctuation) for _ in range(l))


def overwrite_and_delete_file(file: (str, Path)):
    if not isinstance(file, Path):
        file = Path(file)

    if not file.is_file():
        return

    for _ in range(3):
        write_file_0600(
            file=file,
            content=get_random_str(),
        )

    remove_file(file)


def get_ansible_versions() -> str:
    return (f"Python3: {python_version()} | "
            f"Ansible: {get_distribution('ansible').version} | "
            f"Ansible-Core: {get_distribution('ansible-core').version} | "
            f"Ansible-Runner: {get_distribution('ansible-runner').version} |"
            f"Ansible-WebUI: {config['version']}")


# source: https://realpython.com/lru-cache-python/
def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def get_choice_value_by_key(choices: list[tuple], find: any) -> (any, None):
    for k, v in choices:
        if k == find:
            return v

    return None


def get_choice_key_by_value(choices: list[tuple], find: any):
    for k, v in choices:
        if v == find:
            return k

    return None


def unset_or_null(data: dict, key: str) -> bool:
    return key not in data or is_null(data[key])


def pretty_timedelta_str(sec: (int, float)) -> str:
    sec = ceil(sec)
    days, sec = divmod(sec, 86400)
    hours, sec = divmod(sec, 3600)
    minutes, sec = divmod(sec, 60)
    if days > 0:
        return f'{days}d {hours}h {minutes}m {sec}s'

    if hours > 0:
        return f'{hours}h {minutes}m {sec}s'

    if minutes > 0:
        return f'{minutes}m {sec}s'

    return f'{sec}s'

# source: https://validators.readthedocs.io/en/latest/_modules/validators/email.html
EMAIL_REGEX_USER = regex.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+"
    r"(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|'
    r"""\\[\001-\011\013\014\016-\177])*"$)""",
    regex.IGNORECASE
)
EMAIL_REGEX_DOMAIN = regex.compile(
    # domain
    r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)'
    # literal form, ipv4 address (SMTP 4.1.3)
    r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)'
    r'(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',
    regex.IGNORECASE
)


def valid_email(email: str) -> bool:
    if not email or '@' not in email:
        return False

    user_part, domain_part = email.rsplit('@', 1)

    if not EMAIL_REGEX_USER.match(user_part):
        return False

    if not EMAIL_REGEX_DOMAIN.match(domain_part):
        # Try for possible IDN domain-part
        try:
            domain_part = domain_part.encode('idna').decode('ascii')
            return EMAIL_REGEX_DOMAIN.match(domain_part)

        except UnicodeError:
            return False

    return True


def ansible_log_text(line: str) -> str:
    # see: https://medium.com/analytics-vidhya/data-cleaning-for-textual-data-256b4bbffd
    clean = regex.sub(r'[^\x00-\x7F]+', '', line)

    all_chars = (chr(i) for i in range(maxunicode))
    control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
    control_char_re = regex.compile(f'[{regex.escape(control_chars)}]')
    clean = control_char_re.sub('', clean)

    clean = clean.replace("\t", "").replace("\r", "").replace("\n", "")
    clean = regex.sub(r'\s{2,}', '', clean)

    clean = regex.sub(r'["><]', '', clean)
    clean = regex.sub(r'\[\d(|;\d|;\d\d)m', '', clean)
    return clean


ANSIBLE_LOG_COLOR_MAP = {
    '\x1B[0m': '</span>',
    '\x1B[0;32m': '<span class="aw-log-ok">',
    '\x1B[1;32m': '<span class="aw-log-ok">',
    '\x1B[0;36m': '<span class="aw-log-skip">',
    '\x1B[1;36m': '<span class="aw-log-skip">',
    '\x1B[0;35m': '<span class="aw-log-warn">',
    '\x1B[1;35m': '<span class="aw-log-warn">',
    '\x1B[0;31m': '<span class="aw-log-err">',
    '\x1B[1;31m': '<span class="aw-log-err">',
    '\x1B[0;33m': '<span class="aw-log-change">',
    '\x1B[1;33m': '<span class="aw-log-change">',
    '\x1B[0;34m': '<span class="aw-log-debug">',
}


def ansible_log_html(line: str) -> str:
    line = escape_html(line)

    for color_code, color_html in ANSIBLE_LOG_COLOR_MAP.items():
        line = line.replace(color_code, color_html)

    return line


def get_logo() -> str:
    # pylint: disable=C0415
    from aw.settings import STATIC_URL

    url = config['logo_url']
    if not url.startswith('http'):
        return f"{STATIC_URL}{url}"

    return config['logo_url']


def get_client_ip(request) -> str:
    if behind_proxy() or inside_docker():
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For']

        if 'X-Real-IP' in request.headers:
            return request.headers['X-Real-IP ']

    return request.META.get('REMOTE_ADDR')
