import click

from scraperai.cli.controller import Controller


@click.command()
@click.option('--url', prompt='Enter url', help='url of the catalog or product page of any website')
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
        click.echo(f'Unexpected exception: {e}')
        # app.quit()
        raise e


if __name__ == '__main__':
    main()
