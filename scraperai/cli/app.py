import logging

import click

from scraperai.cli.controller import Controller
from scraperai.cli.utils import validate_url


def logging_option(func):
    def callback(ctx, param, value):
        level = getattr(logging, value.upper(), None)
        if level is None:
            raise click.BadParameter(f'Unknown log level: {value}')
        logging.basicConfig(level=level)
        return value

    return click.option('--log-level', default='INFO', show_default=True,
                        expose_value=False, callback=callback,
                        help='Set the logging level')(func)


def validate_url_input(ctx, param, value):
    if validate_url(value):
        return value
    raise click.BadParameter("Invalid URL")


@click.command()
@click.option('--url',
              prompt='Enter url',
              help='url of the catalog or product page of any website',
              callback=validate_url_input)
@logging_option
def main(url: str):
    """ScraperAI CLI Application

    You need openai api key to use this application. There are two ways to pass the key.
    The first is to add OPENAI_API_KEY to your environment or create .env file.
    Second option is to pass api key to the script (you will be asked).
    """
    app = Controller(url)
    try:
        app.run()
    except Exception as e:
        logging.exception(e)
        logging.error(e)
        app.quit(exit_code=-1)


if __name__ == '__main__':
    main()
