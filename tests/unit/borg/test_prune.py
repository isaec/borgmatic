import logging
from collections import OrderedDict

from flexmock import flexmock

from borgmatic.borg import prune as module

from ..test_verbosity import insert_logging_mock


def insert_execute_command_mock(prune_command, output_log_level):
    flexmock(module.environment).should_receive('make_environment')
    flexmock(module).should_receive('execute_command').with_args(
        prune_command,
        output_log_level=output_log_level,
        borg_local_path=prune_command[0],
        extra_environment=None,
    ).once()


BASE_PRUNE_FLAGS = ('--keep-daily', '1', '--keep-weekly', '2', '--keep-monthly', '3')


def test_make_prune_flags_returns_flags_from_config():
    retention_config = OrderedDict((('keep_daily', 1), ('keep_weekly', 2), ('keep_monthly', 3)))
    flexmock(module.feature).should_receive('available').and_return(True)
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())

    result = module.make_prune_flags({}, retention_config, local_borg_version='1.2.3')

    assert result == BASE_PRUNE_FLAGS


def test_make_prune_flags_accepts_prefix_with_placeholders():
    retention_config = OrderedDict(
        (('keep_daily', 1), ('prefix', 'Documents_{hostname}-{now}'))  # noqa: FS003
    )
    flexmock(module.feature).should_receive('available').and_return(True)
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())

    result = module.make_prune_flags({}, retention_config, local_borg_version='1.2.3')

    expected = (
        '--keep-daily',
        '1',
        '--match-archives',
        'sh:Documents_{hostname}-{now}*',  # noqa: FS003
    )

    assert result == expected


def test_make_prune_flags_with_prefix_without_borg_features_uses_glob_archives():
    retention_config = OrderedDict(
        (('keep_daily', 1), ('prefix', 'Documents_{hostname}-{now}'))  # noqa: FS003
    )
    flexmock(module.feature).should_receive('available').and_return(False)
    flexmock(module.flags).should_receive('make_match_archives_flags').and_return(())

    result = module.make_prune_flags({}, retention_config, local_borg_version='1.2.3')

    expected = (
        '--keep-daily',
        '1',
        '--glob-archives',
        'Documents_{hostname}-{now}*',  # noqa: FS003
    )

    assert result == expected


def test_make_prune_flags_prefers_prefix_to_archive_name_format():
    storage_config = {'archive_name_format': 'bar-{now}'}  # noqa: FS003
    retention_config = OrderedDict((('keep_daily', 1), ('prefix', 'bar-')))
    flexmock(module.feature).should_receive('available').and_return(True)
    flexmock(module.flags).should_receive('make_match_archives_flags').never()

    result = module.make_prune_flags(storage_config, retention_config, local_borg_version='1.2.3')

    expected = (
        '--keep-daily',
        '1',
        '--match-archives',
        'sh:bar-*',  # noqa: FS003
    )

    assert result == expected


def test_make_prune_flags_without_prefix_uses_archive_name_format_instead():
    storage_config = {'archive_name_format': 'bar-{now}'}  # noqa: FS003
    retention_config = OrderedDict((('keep_daily', 1), ('prefix', None)))
    flexmock(module.feature).should_receive('available').and_return(True)
    flexmock(module.flags).should_receive('make_match_archives_flags').with_args(
        None, 'bar-{now}', '1.2.3'  # noqa: FS003
    ).and_return(('--match-archives', 'sh:bar-*'))

    result = module.make_prune_flags(storage_config, retention_config, local_borg_version='1.2.3')

    expected = (
        '--keep-daily',
        '1',
        '--match-archives',
        'sh:bar-*',  # noqa: FS003
    )

    assert result == expected


PRUNE_COMMAND = ('borg', 'prune', '--keep-daily', '1', '--keep-weekly', '2', '--keep-monthly', '3')


def test_prune_archives_calls_borg_with_parameters():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('repo',), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_log_info_calls_borg_with_info_parameter():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--info', 'repo'), logging.INFO)
    insert_logging_mock(logging.INFO)

    module.prune_archives(
        repository_path='repo',
        storage_config={},
        dry_run=False,
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_log_debug_calls_borg_with_debug_parameter():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--debug', '--show-rc', 'repo'), logging.INFO)
    insert_logging_mock(logging.DEBUG)

    module.prune_archives(
        repository_path='repo',
        storage_config={},
        dry_run=False,
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_dry_run_calls_borg_with_dry_run_parameter():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--dry-run', 'repo'), logging.INFO)

    module.prune_archives(
        repository_path='repo',
        storage_config={},
        dry_run=True,
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_local_path_calls_borg_via_local_path():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(('borg1',) + PRUNE_COMMAND[1:] + ('repo',), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
        local_path='borg1',
    )


def test_prune_archives_with_remote_path_calls_borg_with_remote_path_parameters():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--remote-path', 'borg1', 'repo'), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
        remote_path='borg1',
    )


def test_prune_archives_with_stats_calls_borg_with_stats_parameter_and_answer_output_log_level():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--stats', 'repo'), module.borgmatic.logger.ANSWER)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
        stats=True,
    )


def test_prune_archives_with_files_calls_borg_with_list_parameter_and_answer_output_log_level():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--list', 'repo'), module.borgmatic.logger.ANSWER)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
        list_archives=True,
    )


def test_prune_archives_with_umask_calls_borg_with_umask_parameters():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    storage_config = {'umask': '077'}
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--umask', '077', 'repo'), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config=storage_config,
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_lock_wait_calls_borg_with_lock_wait_parameters():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    storage_config = {'lock_wait': 5}
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--lock-wait', '5', 'repo'), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config=storage_config,
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )


def test_prune_archives_with_extra_borg_options_calls_borg_with_extra_options():
    flexmock(module.borgmatic.logger).should_receive('add_custom_log_levels')
    flexmock(module.logging).ANSWER = module.borgmatic.logger.ANSWER
    flexmock(module).should_receive('make_prune_flags').and_return(BASE_PRUNE_FLAGS)
    flexmock(module.flags).should_receive('make_repository_flags').and_return(('repo',))
    insert_execute_command_mock(PRUNE_COMMAND + ('--extra', '--options', 'repo'), logging.INFO)

    module.prune_archives(
        dry_run=False,
        repository_path='repo',
        storage_config={'extra_borg_options': {'prune': '--extra --options'}},
        retention_config=flexmock(),
        local_borg_version='1.2.3',
    )
