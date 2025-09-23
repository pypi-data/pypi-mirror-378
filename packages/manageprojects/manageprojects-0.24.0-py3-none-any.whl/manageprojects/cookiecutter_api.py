import logging
from pathlib import Path
from unittest.mock import patch

from bx_py_utils.path import assert_is_dir
from cli_base.cli_tools.git import Git
from cookiecutter.config import get_user_config
from cookiecutter.main import cookiecutter
from cookiecutter.repository import determine_repo_dir

from manageprojects.utilities.cookiecutter_utils import GenerateFilesWrapper
from manageprojects.utilities.log_utils import log_func_call


logger = logging.getLogger(__name__)


def get_repo_path(
    *,
    template: str,  # CookieCutter Template path or GitHub url
    directory: str | None = None,  # Directory name of the CookieCutter Template
    checkout: str | None = None,  # The branch, tag or commit ID to checkout after clone
    password: str | None = None,  # Optional password to use when extracting the repository
    config_file: Path | None = None,  # Optional path to 'cookiecutter_config.yaml'
) -> Path:
    """
    Checkout the cookiecutter template and reset it to `checkout` if needed.
    """
    if directory:
        assert '://' not in directory
        assert template != directory

    config_dict = log_func_call(
        logger=logger,
        func=get_user_config,
        config_file=config_file,
        default_config=None,
    )
    repo_dir, cleanup = determine_repo_dir(
        template=template,
        directory=directory,
        abbreviations=config_dict['abbreviations'],
        clone_to_dir=config_dict['cookiecutters_dir'],
        checkout=checkout,
        no_input=True,
        password=password,
    )
    logger.debug('repo_dir: %s', repo_dir)

    repo_path = Path(repo_dir)
    assert_is_dir(repo_path)

    if checkout is not None:
        # Cookiecutter will only checkout a specific commit, if `template` is a repro url!

        git = Git(cwd=repo_path, detect_root=True)
        assert repo_path.is_relative_to(git.cwd), f'Git repro {git.cwd} is not {repo_path}'
        # assert git.cwd == repo_path, f'Git repro {git.cwd} is not {repo_path}'
        current_hash = git.get_current_hash(verbose=True)
        if current_hash != checkout:
            git.reset(commit=checkout, verbose=True)

    return repo_path


def execute_cookiecutter(
    *,
    template: str,  # CookieCutter Template path or GitHub url
    directory: str | None = None,  # Directory name of the CookieCutter Template
    output_dir: Path,  # Target path where CookieCutter should store the result files
    no_input: bool = False,  # Prompt the user at command line for manual configuration?
    extra_context: dict | None = None,
    replay: bool | None = None,
    checkout: str | None = None,  # Optional branch, tag or commit ID to checkout after clone
    password: str | None = None,  # Optional password to use when extracting the repository
    config_file: Path | None = None,  # Optional path to 'cookiecutter_config.yaml'
) -> tuple[dict, Path, Path]:
    """
    "Just" run cookiecutter
    """
    repo_path = get_repo_path(
        template=template,
        directory=directory,
        checkout=checkout,
        password=password,
        config_file=config_file,
    )
    generate_files_wrapper = GenerateFilesWrapper()
    with patch('cookiecutter.main.generate_files', generate_files_wrapper):
        destination = log_func_call(
            logger=logger,
            func=cookiecutter,
            template=template,
            directory=directory,
            output_dir=output_dir,
            no_input=no_input,
            extra_context=extra_context,
            replay=replay,
            checkout=checkout,
            password=password,
            config_file=config_file,
        )
    cookiecutter_context = generate_files_wrapper.context
    logger.info('Cookiecutter context: %r', cookiecutter_context)
    destination_path = Path(destination)
    assert_is_dir(destination_path)
    logger.info('Cookiecutter generated here: %r', destination_path)
    return cookiecutter_context, destination_path, repo_path
