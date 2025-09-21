# -*- coding: utf-8; -*-
"""
Rattail Demo Commands
"""

import datetime
import logging
import os
import shutil

import typer
from typing_extensions import Annotated

from rattail.commands.typer import (make_typer, typer_get_runas_user,
                                    importer_command, file_exporter_command)
from rattail.commands.importing import ImportCommandHandler
from rattail.commands.purging import run_purge


log = logging.getLogger(__name__)

# nb. this is the top-level command
rattail_demo_typer = make_typer(
    name='rattail_demo',
    help="Rattail Demo (custom Rattail system)"
)


@rattail_demo_typer.command()
@file_exporter_command
def export_shopfoo(
        ctx: typer.Context,
        **kwargs
):
    """
    Export data to the Harvest system
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    handler = ImportCommandHandler(
        config, import_handler_spec='rattail_demo.shopfoo.importing.rattail:FromRattailToShopfoo')
    kwargs['user'] = typer_get_runas_user(ctx)
    kwargs['handler_kwargs'] = {'output_dir': kwargs['output_dir']}
    handler.run(kwargs, progress=progress)


@rattail_demo_typer.command()
@importer_command
def import_self(
        ctx: typer.Context,
        **kwargs
):
    """
    Update "cascading" Rattail data based on "core" Rattail data
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    handler = ImportCommandHandler(
        config, import_handler_spec='rattail_demo.importing.local:FromRattailDemoToSelf')
    kwargs['user'] = typer_get_runas_user(ctx)
    handler.run(kwargs, progress=progress)


@rattail_demo_typer.command()
def purge_shopfoo(
        ctx: typer.Context,
        before: Annotated[
            datetime.datetime,
            typer.Option(formats=['%Y-%m-%d'],
                         help="Use this date as cutoff, i.e. purge all data "
                         "*before* this date.  If not specified, will use "
                         "--before-days to calculate instead.")] = None,
        before_days: Annotated[
            int,
            typer.Option(help="Calculate the cutoff date by subtracting this "
                         "number of days from the current date, i.e. purge all "
                         "data *before* the resulting date.  Note that if you "
                         "specify --before then that date will be used instead "
                         "of calculating one from --before-days.  If neither is "
                         "specified then --before-days is used, with its default "
                         "value.")] = 90,
        dry_run: Annotated[
            bool,
            typer.Option('--dry-run',
                         help="Go through the full motions and allow logging "
                         "etc. to occur, but rollback (abort) the transaction "
                         "at the end.")] = False,
):
    """
    Purge old Shopfoo export data
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    app = config.get_app()
    model = app.model

    def finder(session, cutoff, dry_run=False):
        return session.query(model.ShopfooProductExport)\
                      .filter(model.ShopfooProductExport.created < app.make_utc(cutoff))\
                      .all()

    def purger(session, export, cutoff, dry_run=False):
        uuid = export.uuid
        log.debug("purging export object %s: %s", uuid, export)
        session.delete(export)

        # maybe delete associated files
        if not dry_run:
            session.flush()
            key = model.ShopfooProductExport.export_key
            path = config.export_filepath(key, uuid)
            if os.path.exists(path):
                shutil.rmtree(path)

        return True

    run_purge(config, "Shopfoo Export", "Shopfoo Exports",
              finder, purger,
              before=before.date() if before else None,
              before_days=before_days,
              default_before_days=90,
              dry_run=dry_run, progress=progress)


@rattail_demo_typer.command()
def install(
        ctx: typer.Context,
):
    """
    Install the Rattail Demo app
    """
    from rattail.install import InstallHandler

    config = ctx.parent.rattail_config
    handler = InstallHandler(config,
                             app_title="Rattail Demo",
                             app_package='rattail_demo',
                             app_eggname='rattail_demo',
                             app_pypiname='rattail_demo')
    handler.run()
