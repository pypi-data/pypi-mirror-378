# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tempmon commands
"""

import datetime
import logging
from enum import Enum
from pathlib import Path

import typer
from typing_extensions import Annotated

from rattail.commands import rattail_typer
from rattail.commands.typer import importer_command, typer_get_runas_user
from rattail.commands.importing import ImportCommandHandler


log = logging.getLogger(__name__)


class ServiceAction(str, Enum):
    start = 'start'
    stop = 'stop'


@rattail_typer.command()
@importer_command
def export_hotcooler(
        ctx: typer.Context,
        **kwargs
):
    """
    Export data from Rattail-Tempmon to HotCooler
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    handler = ImportCommandHandler(
        config,
        import_handler_spec='rattail_tempmon.hotcooler.importing.tempmon:FromTempmonToHotCooler')
    kwargs['user'] = typer_get_runas_user(ctx)
    handler.run(kwargs, progress=progress)


@rattail_typer.command()
def purge_tempmon(
        ctx: typer.Context,
        keep_days: Annotated[
            int,
            typer.Option('--keep',
                         help="Number of days for which data should be kept.")] = ...,
        dry_run: Annotated[
            bool,
            typer.Option('--dry-run',
                         help="Go through the full motions and allow logging etc. to "
                         "occur, but rollback (abort) the transaction at the end.")] = False,
):
    """
    Purge stale data from Tempmon database
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    do_purge(config, keep_days, dry_run=dry_run, progress=progress)


@rattail_typer.command()
def tempmon_client(
        ctx: typer.Context,
        action: Annotated[
            ServiceAction,
            typer.Argument(help="Action to perform for the service.")] = ...,
        pidfile: Annotated[
            Path,
            typer.Option('--pidfile', '-p',
                         help="Path to PID file.")] = None,
        # TODO: deprecate / remove this
        daemonize: Annotated[
            bool,
            typer.Option('--daemonize',
                         help="Daemonize when starting.")] = False,
):
    """
    Manage the tempmon-client daemon
    """
    from rattail_tempmon.client import make_daemon

    config = ctx.parent.rattail_config
    daemon = make_daemon(config, pidfile)
    if action == 'start':
        daemon.start(daemonize)
    elif action == 'stop':
        daemon.stop()


@rattail_typer.command()
def tempmon_problems(
        ctx: typer.Context,
):
    """
    Email report(s) of various Tempmon data problems
    """
    from rattail_tempmon import problems

    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    problems.disabled_probes(config, progress=progress)


@rattail_typer.command()
def tempmon_server(
        ctx: typer.Context,
        action: Annotated[
            ServiceAction,
            typer.Argument(help="Action to perform for the service.")] = ...,
        pidfile: Annotated[
            Path,
            typer.Option('--pidfile', '-p',
                         help="Path to PID file.")] = None,
        # TODO: deprecate / remove this
        daemonize: Annotated[
            bool,
            typer.Option('--daemonize',
                         help="Daemonize when starting.")] = False,
):
    """
    Manage the tempmon-server daemon
    """
    from rattail_tempmon.server import make_daemon

    config = ctx.parent.rattail_config
    daemon = make_daemon(config, pidfile)
    if action == 'start':
        daemon.start(daemonize)
    elif action == 'stop':
        daemon.stop()


def do_purge(config, keep_days, dry_run=False, progress=None):
    from rattail_tempmon.db import Session, model
    from rattail.db.util import finalize_session

    app = config.get_app()
    cutoff = app.today() - datetime.timedelta(days=keep_days)
    cutoff = app.localtime(datetime.datetime.combine(cutoff, datetime.time(0)))
    session = Session()

    readings = session.query(model.Reading)\
                      .filter(model.Reading.taken < app.make_utc(cutoff))\
                      .all()

    def purge(reading, i):
        session.delete(reading)
        if i % 200 == 0:
            session.flush()

    app.progress_loop(purge, readings, progress,
                      message="Purging stale readings")
    log.info("deleted %s stale readings", len(readings))
    finalize_session(session, dry_run=dry_run)
