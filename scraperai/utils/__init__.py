from urllib.parse import urlparse

import tiktoken


def cut_large_request(system_prompt: str,
                      prompt: str,
                      max_tokens: int,
                      response_tokens: int,
                      step: float = 0.9) -> str:
    encoding = tiktoken.encoding_for_model('gpt-4-0125-preview')
    fixed_size = len(encoding.encode(system_prompt)) + response_tokens
    available_size = max_tokens - fixed_size
    payload_size = len(encoding.encode(prompt))
    if available_size <= 0:
        raise Exception('Prompt is too large!')
    if fixed_size + payload_size >= max_tokens:
        return cut_large_request(system_prompt, prompt[0: int(len(prompt) * step)], max_tokens, response_tokens, step)
    return prompt


def fix_relative_url(base_url: str, url: str) -> str:
    components = urlparse(base_url)
    base_url = components.scheme + '://' + components.netloc + '/'
    if url.startswith('http'):
        return url
    return base_url + url.lstrip('/')
