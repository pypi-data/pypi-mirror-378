from pathlib import Path
from shutil import rmtree
from re import sub as regex_replace

from django.utils import timezone

from aw.config.main import config
from aw.config.hardcoded import REPO_CLONE_TIMEOUT, FILE_TIME_FORMAT
from aw.model.job import  JobExecution
from aw.utils.util import is_null, is_set, write_file_0640, datetime_w_tz
from aw.utils.subps import process
from aw.execute.play_credentials import write_pwd_file, get_pwd_file
from aw.execute.util import update_status, create_dirs
from aw.utils.handlers import AnsibleRepositoryError
from aw.model.repository import Repository
from aw.model.base import JOB_EXEC_STATUS_FAILED
from aw.utils.db_handler import close_old_mysql_connections


class ExecuteRepository:
    ISOLATE_BROWSABLE = 'isolated'

    def __init__(self, repository: Repository, execution: JobExecution = None, path_run: Path = None):
        self.repository = repository
        self.path_run = path_run
        self.execution = execution
        self.path_repo = None
        self.isolate_subdir = self.execution.id if self.execution is not None else self.ISOLATE_BROWSABLE
        create_dirs(path=config['path_log'], desc='log')

    def create_repository(self, env: dict):
        if is_set(self.repository.git_override_initialize):
            self._run_repo_hooks(
                cmds=self.repository.git_override_initialize,
                env=env,
            )
            return

        git_clone = ['git', 'clone', '--branch', self.repository.git_branch]

        if is_set(self.repository.git_limit_depth):
            git_clone.extend(['--depth', str(self.repository.git_limit_depth)])

        if self.path_repo is None:
            self.path_repo = self.get_path_repo()

        git_clone.extend([self._git_origin_with_credentials(), str(self.path_repo)])

        git_cmds = [' '.join(git_clone)]

        if self.repository.git_lfs:
            git_cmds.append('git lfs fetch')
            git_cmds.append('git lfs checkout')

        try:
            for cmd in git_cmds:
                self._repo_process(cmd=cmd, env=env)

        except AnsibleRepositoryError:
            self.update_repository(env)

    def update_repository(self, env: dict):
        if is_set(self.repository.git_override_update):
            self._run_repo_hooks(
                cmds=self.repository.git_override_update,
                env=env,
            )
            return

        git_pull = ['git', 'pull']

        if is_set(self.repository.git_limit_depth):
            git_pull.extend(['--depth', str(self.repository.git_limit_depth)])

        git_cmds = [
            'git reset --hard',
            ' '.join(git_pull),
        ]

        if self.repository.git_lfs:
            git_cmds.append('git lfs fetch')
            git_cmds.append('git lfs checkout')

        for cmd in git_cmds:
            self._repo_process(cmd=cmd, env=env)

    def create_or_update_repository(self):
        if is_null(self.repository) or self.repository.rtype_name == 'Static':
            return

        if self.execution is not None:
            self.repository.log_stderr = self.execution.log_stderr_repo
            self.repository.log_stdout = self.execution.log_stdout_repo

        else:
            self._logs_init()

        close_old_mysql_connections()
        self.repository.save()

        try:
            update_status(self.repository, status='Running')
            path_repo = self.get_path_repo()

            env = self._git_env()
            if len(env) > 0:
                self._log_file_write(f"USING ENVIRONMENT: {env}")

            self._run_repo_hooks(cmds=self.repository.git_hook_pre, env=env)

            if not (Path(path_repo) / '.git').is_dir():
                self.create_repository(env=env)

            else:
                self.update_repository(env=env)

            self.repository.time_update = timezone.now()

            self._run_repo_hooks(cmds=self.repository.git_hook_post, env=env)

            update_status(self.repository, status='Finished')

        # pylint: disable=W0718
        except Exception as err:
            self._error(msg=f"Got unexpected error: '{err}'")

    def _error(self, msg: str):
        write_file_0640(file=self.repository.log_stderr, content=msg)
        update_status(self.repository, status=JOB_EXEC_STATUS_FAILED)
        raise AnsibleRepositoryError(msg).with_traceback(None) from None

    def get_path_run_repo(self) -> Path:
        return self.path_run / '.repository'

    def _git_env(self) -> dict:
        env = {
            'GIT_SSH_COMMAND': 'ssh -o ConnectTimeout=10',
            'GIT_HTTP_CONNECT_TIMEOUT': '10',
        }
        if self.repository.git_origin.find(' -p') != -1:
            try:
                self.repository.git_origin, port = self.repository.git_origin.split(' -p')
                env['GIT_SSH_COMMAND'] += f" -p {port}"

            except IndexError:
                pass

        if is_set(self.repository.git_credentials) and is_set(self.repository.git_credentials.ssh_key):
            path_run_repo = self.get_path_run_repo()
            path_run_repo.mkdir(mode=0o700, parents=True, exist_ok=True)
            write_pwd_file(credentials=self.repository.git_credentials, attr='ssh_key', path_run=path_run_repo)
            env['GIT_SSH_COMMAND'] += f" -i {get_pwd_file(path_run=path_run_repo, attr='ssh_key')}"

        if is_set(config['path_ssh_known_hosts']):
            if Path(config['path_ssh_known_hosts']).is_file():
                env['GIT_SSH_COMMAND'] += f" -o UserKnownHostsFile={config['path_ssh_known_hosts']}"

            else:
                self._log_file_write('Ignoring known_hosts file because it does not exist')

        if env['GIT_SSH_COMMAND'] == 'ssh':
            env.pop('GIT_SSH_COMMAND')

        return env

    def get_project_dir(self) -> str:
        if is_null(self.repository):
            return config['path_play']

        return str(self.get_path_playbook_base())

    def cleanup_repository(self):
        if is_null(self.repository) or self.repository.rtype_name == 'Static':
            return

        self._run_repo_hooks(cmds=self.repository.git_hook_cleanup, env=self._git_env())
        if self.repository.git_isolate and self.isolate_subdir != self.ISOLATE_BROWSABLE:
            rmtree(self.get_path_repo(), ignore_errors=True)

    def get_path_repo(self) -> Path:
        path_repo = get_path_repo_wo_isolate(self.repository)

        if self.repository.git_isolate:
            path_repo = path_repo / str(self.isolate_subdir)
            path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)

        return path_repo

    def get_path_playbook_base(self) -> Path:
        path_repo = self.get_path_repo()
        if self.repository.rtype_name == 'Git' and is_set(self.repository.git_playbook_base):
            path_repo = path_repo / self.repository.git_playbook_base

        return path_repo

    def _repo_process(self, cmd: str, env: dict, hook: bool = False):
        if self.path_repo is None:
            self.path_repo = self.get_path_repo()

        if not hook:
            cmd = f'timeout {self.repository.git_timeout} {cmd}'

        result = process(cmd=cmd, cwd=self.path_repo, env=env, shell=True, timeout_sec=REPO_CLONE_TIMEOUT)
        self._log_file_write(f"COMMAND: {cmd}\n{result['stdout']}")
        if result['rc'] != 0:
            self._error(
                f"Repository command failed: '{cmd}'\n"
                f"Got error: '{result['stderr']}'\n"
                f"Got output: '{result['stdout']}'"
            )

    def _run_repo_hooks(self, cmds: str, env: dict):
        if is_set(cmds):
            for cmd in cmds.split(','):
                self._repo_process(cmd=cmd, env=env, hook=True)

    def _git_origin_with_credentials(self) -> str:
        origin = self.repository.git_origin

        if is_set(self.repository.git_credentials):
            credentials = self.repository.git_credentials

            if origin.find('://') != -1 and origin.find('ssh://') == -1:
                # not ssh
                if origin.find('@') == -1:
                    proto, origin_host = origin.split('://', 1)
                    if is_set(credentials.connect_user) and is_set(credentials.connect_pass):
                        origin = f'{proto}://{credentials.connect_user}:{credentials.connect_pass}@{origin_host}'

                    elif is_set(credentials.connect_pass):
                        # token authentication
                        origin = f'{proto}://{credentials.connect_pass}@{origin_host}'

            else:
                # ssh
                if origin.find('@') == -1 and is_set(credentials.connect_user):
                    origin = f'{credentials.connect_user}@{origin}'

        return origin

    def _log_file_write(self, content: str):
        if self.repository.log_stdout is None:
            return

        write_file_0640(
            file=self.repository.log_stdout,
            content=f"{content}\n"
        )

    def _logs_init(self):
        safe_repo_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=self.repository.name)
        timestamp = datetime_w_tz().strftime(FILE_TIME_FORMAT)
        log_file = f"{config['path_log']}/repo_{safe_repo_name}_{timestamp}"
        self.repository.log_stdout = f'{log_file}_stdout_repo.log'
        self.repository.log_stderr = f'{log_file}_stderr_repo.log'


def get_path_repo_wo_isolate(repository: Repository) -> Path:
    if repository.rtype_name == 'Static':
        return repository.static_path

    safe_repo_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=repository.name)
    path_repo = Path(config['path_run']) / 'repositories' / safe_repo_name
    path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)
    return path_repo
