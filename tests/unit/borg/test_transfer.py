import logging

import pytest
from flexmock import flexmock

from borgmatic.borg import transfer as module

from ..test_verbosity import insert_logging_mock


def test_transfer_archives_calls_borg_with_flags():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_dry_run_calls_borg_with_dry_run_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags').with_args('dry-run', True).and_return(
        ('--dry-run',)
    )
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--repo', 'repo', '--dry-run'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=True,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_log_info_calls_borg_with_info_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--info', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )
    insert_logging_mock(logging.INFO)
    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_log_debug_calls_borg_with_debug_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--debug', '--show-rc', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )
    insert_logging_mock(logging.DEBUG)

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_archive_calls_borg_with_match_archives_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').with_args(
        'archive', 'bar-{now}', '2.3.4'  # noqa: FS003
    ).and_return(('--match-archives', 'archive'))
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--match-archives', 'archive', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={'archive_name_format': 'bar-{now}'},  # noqa: FS003
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive='archive', progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_match_archives_calls_borg_with_match_archives_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').with_args(
        'sh:foo*', 'bar-{now}', '2.3.4'  # noqa: FS003
    ).and_return(('--match-archives', 'sh:foo*'))
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--match-archives', 'sh:foo*', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={'archive_name_format': 'bar-{now}'},  # noqa: FS003
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives='sh:foo*', source_repository=None
        ),
    )


def test_transfer_archives_with_archive_name_format_calls_borg_with_match_archives_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').with_args(
        None, 'bar-{now}', '2.3.4'  # noqa: FS003
    ).and_return(('--match-archives', 'sh:bar-*'))
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--match-archives', 'sh:bar-*', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={'archive_name_format': 'bar-{now}'},  # noqa: FS003
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_local_path_calls_borg_via_local_path():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg2', 'transfer', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg2',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
        local_path='borg2',
    )


def test_transfer_archives_with_remote_path_calls_borg_with_remote_path_flags():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags').with_args(
        'remote-path', 'borg2'
    ).and_return(('--remote-path', 'borg2'))
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--remote-path', 'borg2', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
        remote_path='borg2',
    )


def test_transfer_archives_with_lock_wait_calls_borg_with_lock_wait_flags():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags').with_args('lock-wait', 5).and_return(
        ('--lock-wait', '5')
    )
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    storage_config = {'lock_wait': 5}
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--lock-wait', '5', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config=storage_config,
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository=None
        ),
    )


def test_transfer_archives_with_progress_calls_borg_with_progress_flag():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(('--progress',))
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--progress', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=module.DO_NOT_CAPTURE,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=True, match_archives=None, source_repository=None
        ),
    )


@pytest.mark.parametrize('argument_name', ('upgrader', 'sort_by', 'first', 'last'))
def test_transfer_archives_passes_through_arguments_to_borg(argument_name):
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flag_name = f"--{argument_name.replace('_', ' ')}"
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(
        (flag_name, 'value')
    )
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', flag_name, 'value', '--repo', 'repo'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None,
            progress=None,
            match_archives=None,
            source_repository=None,
            **{argument_name: 'value'},
        ),
    )


def test_transfer_archives_with_source_repository_calls_borg_with_other_repo_flags():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.flags).should_receive('make_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags').with_args('other-repo', 'other').and_return(
        ('--other-repo', 'other')
    )
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())
    flexmock(module.flags).should_receive('make_flags_from_arguments').and_return(())
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('--repo', 'repo'))
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        ('borg', 'transfer', '--repo', 'repo', '--other-repo', 'other'),
        output_log_level=module.borgmatic.logger.ANSWER,
        output_file=None,
        borg_local_path='borg',
        extra_environment=None,
    )

    module.transfer_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        local_borg_version='2.3.4',
        transfer_arguments=flexmock(
            archive=None, progress=None, match_archives=None, source_repository='other'
        ),
    )
