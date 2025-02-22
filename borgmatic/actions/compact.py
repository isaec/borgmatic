import logging

import borgmatic.borg.compact
import borgmatic.borg.feature
import borgmatic.config.validate
import borgmatic.hooks.command

logger = logging.getLogger(__name__)


def run_compact(
    config_filename,
    repository,
    storage,
    retention,
    hooks,
    hook_context,
    local_borg_version,
    compact_arguments,
    global_arguments,
    dry_run_label,
    local_path,
    remote_path,
):
    '''
    Run the "compact" action for the given repository.
    '''
    if compact_arguments.repository and not borgmatic.config.validate.repositories_match(
        repository, compact_arguments.repository
    ):
        return

    borgmatic.hooks.command.execute_hook(
        hooks.get('before_compact'),
        hooks.get('umask'),
        config_filename,
        'pre-compact',
        global_arguments.dry_run,
        **hook_context,
    )
    if borgmatic.borg.feature.available(borgmatic.borg.feature.Feature.COMPACT, local_borg_version):
        logger.info(f'{repository["path"]}: Compacting segments{dry_run_label}')
        borgmatic.borg.compact.compact_segments(
            global_arguments.dry_run,
            repository['path'],
            storage,
            local_borg_version,
            local_path=local_path,
            remote_path=remote_path,
            progress=compact_arguments.progress,
            cleanup_commits=compact_arguments.cleanup_commits,
            threshold=compact_arguments.threshold,
        )
    else:  # pragma: nocover
        logger.info(f'{repository["path"]}: Skipping compact (only available/needed in Borg 1.2+)')
    borgmatic.hooks.command.execute_hook(
        hooks.get('after_compact'),
        hooks.get('umask'),
        config_filename,
        'post-compact',
        global_arguments.dry_run,
        **hook_context,
    )
