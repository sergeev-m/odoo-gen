import click

from .app import OdooGenApp


@click.command()
@click.argument('model')
@click.argument('path', required=False, type=click.Path())
@click.option('-m', '--menu', is_flag=True, help='create an menu')
@click.option('--no-views', is_flag=True, help="don't create views")
@click.option('-v', '--verbose', is_flag=True)
@click.option('-f', '--force', is_flag=True, help='overwrite existing files')
@click.option('--skip-existing', is_flag=True, help='skip existing files')
@click.option('--debug', is_flag=True, help='enable debug mode')
def main(model, path, menu, no_views, verbose, force, skip_existing, debug):
    app = OdooGenApp(
        model=model,
        path=path,
        verbose=verbose,
        menu=menu,
        no_views=no_views,
        force=force,
        skip_existing=skip_existing,
        debug=debug
    )
    app.run()

    click.secho("Done", fg="green")
     

# if __name__ == "__main__":
#     main()
