import logging

import borgmatic.logger
from borgmatic.borg import environment, feature, flags
from borgmatic.execute import execute_command

logger = logging.getLogger(__name__)


def make_prune_flags(storage_config, retention_config, local_borg_version):
    '''
    Given a retention config dict mapping from option name to value, transform it into an sequence of
    command-line flags.

    For example, given a retention config of:

        {'keep_weekly': 4, 'keep_monthly': 6}

    This will be returned as an iterable of:

        (
            ('--keep-weekly', '4'),
            ('--keep-monthly', '6'),
        )
    '''
    config = retention_config.copy()
    prefix = config.pop('prefix', None)

    flag_pairs = (
        ('--' + option_name.replace('_', '-'), str(value)) for option_name, value in config.items()
    )

    return tuple(element for pair in flag_pairs for element in pair) + (
        (
            ('--match-archives', f'sh:{prefix}*')
            if feature.available(feature.Feature.MATCH_ARCHIVES, local_borg_version)
            else ('--glob-archives', f'{prefix}*')
        )
        if prefix
        else (
            flags.make_match_archives_flags(
                storage_config.get('match_archives'),
                storage_config.get('archive_name_format'),
                local_borg_version,
            )
        )
    )


def prune_archives(
    dry_run,
    repository_path,
    storage_config,
    retention_config,
    local_borg_version,
    local_path='borg',
    remote_path=None,
    stats=False,
    list_archives=False,
):
    '''
    Given dry-run flag, a local or remote repository path, a storage config dict, and a
    retention config dict, prune Borg archives according to the retention policy specified in that
    configuration.
    '''
    borgmatic.logger.add_custom_log_levels()
    umask = storage_config.get('umask', None)
    lock_wait = storage_config.get('lock_wait', None)
    extra_borg_options = storage_config.get('extra_borg_options', {}).get('prune', '')

    full_command = (
        (local_path, 'prune')
        + make_prune_flags(storage_config, retention_config, local_borg_version)
        + (('--remote-path', remote_path) if remote_path else ())
        + (('--umask', str(umask)) if umask else ())
        + (('--lock-wait', str(lock_wait)) if lock_wait else ())
        + (('--stats',) if stats and not dry_run else ())
        + (('--info',) if logger.getEffectiveLevel() == logging.INFO else ())
        + (('--list',) if list_archives else ())
        + (('--debug', '--show-rc') if logger.isEnabledFor(logging.DEBUG) else ())
        + (('--dry-run',) if dry_run else ())
        + (tuple(extra_borg_options.split(' ')) if extra_borg_options else ())
        + flags.make_repository_flags(repository_path, local_borg_version)
    )

    if stats or list_archives:
        output_log_level = logging.ANSWER
    else:
        output_log_level = logging.INFO

    execute_command(
        full_command,
        output_log_level=output_log_level,
        borg_local_path=local_path,
        extra_environment=environment.make_environment(storage_config),
    )
