from pathlib import Path
from string import digits
from datetime import datetime
from re import sub as regex_replace
from random import choice as random_choice

from aw.config.main import config
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.utils.handlers import AnsibleConfigError
from aw.model.job import JobExecution, Job
from aw.model.repository import Repository
from aw.utils.util import datetime_w_tz
from aw.utils.db_handler import close_old_mysql_connections


def config_error(msg: str):
    raise AnsibleConfigError(msg).with_traceback(None) from None


def decode_job_env_vars(env_vars_csv: str, src: str) -> dict:
    try:
        env_vars = {}
        for kv in env_vars_csv.split(','):
            k, v = kv.split('=')
            env_vars[k] = v

        return env_vars

    except ValueError:
        config_error(
            f"Environmental variables of {src} are not in a valid format "
            f"(comma-separated key-value pairs). Example: 'key1=val1,key2=val2'"
        )
        return {}


def update_status(obj: (JobExecution, Repository), status: (str, int)):
    if isinstance(status, str):
        status = obj.status_id_from_name(status)

    obj.status = status
    close_old_mysql_connections()
    obj.save()


def is_execution_status(execution: JobExecution, status: str) -> bool:
    close_old_mysql_connections()
    is_status = JobExecution.objects.get(id=execution.id).status
    check_status = execution.status_id_from_name(status)
    return is_status == check_status


def get_path_run() -> Path:
    # build unique temporary execution directory
    path_run = config['path_run']
    if not path_run.endswith('/'):
        path_run += '/'

    path_run += datetime.now().strftime(FILE_TIME_FORMAT)
    path_run += ''.join(random_choice(digits) for _ in range(5))
    return Path(path_run)


def create_dirs(path: (str, Path), desc: str):
    try:
        if not isinstance(path, Path):
            path = Path(path)

        path.mkdir(mode=0o750, parents=True, exist_ok=True)

    except (OSError, FileNotFoundError):
        raise OSError(f"Unable to created {desc} directory: '{path}'").with_traceback(None) from None


def job_logs(job: Job, execution: JobExecution) -> dict:
    safe_job_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=job.name)
    safe_user_name = execution.user_name.replace('.', '_')
    safe_user_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=safe_user_name)

    timestamp = datetime_w_tz().strftime(FILE_TIME_FORMAT)
    log_file = f"{config['path_log']}/{safe_job_name}_{timestamp}_{safe_user_name}"

    log_files = {
        'stdout': f'{log_file}_stdout.log',
        'stderr': f'{log_file}_stderr.log',
        'stdout_repo': f'{log_file}_stdout_repo.log',
        'stderr_repo': f'{log_file}_stderr_repo.log',
    }

    execution.log_stdout = log_files['stdout']
    execution.log_stderr = log_files['stderr']
    execution.log_stdout_repo = log_files['stdout_repo']
    execution.log_stderr_repo = log_files['stderr_repo']

    return log_files
