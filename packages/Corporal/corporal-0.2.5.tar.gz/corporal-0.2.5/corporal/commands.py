# -*- coding: utf-8; -*-
"""
Corporal commands
"""

import typer

from rattail.commands.typer import make_typer


# nb. this is the top-level command for corporal
corporal_typer = make_typer(
    name='corporal',
    help="Corporal (custom Rattail system)"
)


@corporal_typer.command()
def install(
        ctx: typer.Context,
):
    """
    Install the Corporal app
    """
    from rattail.install import InstallHandler

    config = ctx.parent.rattail_config
    handler = InstallHandler(config,
                             app_title="Corporal",
                             app_package='corporal',
                             app_eggname='Corporal',
                             app_pypiname='Corporal')
    handler.run()
