from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


def fix_relative_url(base_url: str, url: str) -> str:
    components = urlparse(base_url)
    base_url = components.scheme + '://' + components.netloc + '/'
    if url.startswith('http'):
        return url
    return base_url + url.lstrip('/')


def get_url_query_param_value(url: str, param_name: str) -> list[str] | None:
    url_parts = urlparse(url)
    query = parse_qs(url_parts.query)
    return query.get(param_name)


def add_or_replace_url_param(url: str, param_name: str, param_value: str | int) -> str:
    """
    Adds or replaces a query parameter to/in the URL.

    Args:
    - url (str): The URL to modify.
    - param_name (str): The name of the parameter to add or replace.
    - param_value (str): The value of the parameter.

    Returns:
    - str: The modified URL with the new or updated query parameter.
    """
    url_parts = urlparse(url)
    query = parse_qs(url_parts.query)
    query[param_name] = [param_value]
    url_parts = list(url_parts)
    url_parts[4] = urlencode(query, doseq=True)
    return urlunparse(url_parts)
