from .app import app, socketio, initialization
from os.path import isfile
import click

@click.command
@click.option('-c', '--config', default=None, help='Path to the config file.')
def main(config):
    '''Entry point for YACS.'''
    if config is not None:
        if not isfile(config):
            click.echo('Config file does not exist!', err=True)
            return 0
    result = initialization(config)
    if result != 'ok':
        click.echo(f'Initialization failed while parsing config file: {result}')
        return 0
    app.logger.info(f'YACS is now running on http://{app.config["app"]["ip"]}:{app.config["app"]["port"]}{' with DEBUG MODE ON' if app.config['DEBUG'] else ''}.')
    app.logger.info(f'You have set the guest passphrase to "{app.config['app']['user_phrase']}" , and the admin passphrase to "{app.config['app']['admin_phrase']}"')
    socketio.run(
        app,
        host=app.config["app"]["ip"],
        port=app.config["app"]["port"],
        debug=app.config["DEBUG"],
    )