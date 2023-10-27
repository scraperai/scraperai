from io import StringIO

import pandas as pd
import tiktoken

from llm.chat import OpenAIModel

models_max_tokens = {
    OpenAIModel.gpt4: 8192,
    OpenAIModel.gpt3: 4097,
    OpenAIModel.gpt3_large: 16385
}


def split_large_request(model: OpenAIModel,
                        system_prompt: str,
                        prompt: str,
                        payload: str,
                        response_tokens: int) -> list[str]:
    encoding = tiktoken.encoding_for_model(OpenAIModel.gpt4.value)
    fixed_size = len(encoding.encode(system_prompt + prompt)) + response_tokens
    available_size = models_max_tokens[model] - fixed_size
    payload_size = len(encoding.encode(payload))
    if available_size <= 0:
        raise Exception('Prompt is too large!')
    chunks = payload_size // available_size + 1
    chunk_size = len(payload) // chunks
    return [payload[i * chunk_size: (i + 1) * chunk_size] for i in range(chunks)]


def cut_large_request(model: OpenAIModel,
                      system_prompt: str,
                      prompt: str,
                      payload: str,
                      response_tokens: int,
                      step: float = 0.9) -> str:
    encoding = tiktoken.encoding_for_model(OpenAIModel.gpt4.value)
    fixed_size = len(encoding.encode(system_prompt + prompt)) + response_tokens
    available_size = models_max_tokens[model] - fixed_size
    payload_size = len(encoding.encode(payload))
    if available_size <= 0:
        raise Exception('Prompt is too large!')
    if fixed_size + payload_size >= models_max_tokens[model]:
        return cut_large_request(model, system_prompt, prompt,
                                 payload[0: int(len(payload) * step)], response_tokens, step)
    return payload


def markdown_to_pandas(text: str, subs: dict[str, str]) -> pd.DataFrame:
    df = pd.read_csv(StringIO(text), sep='|', index_col=1).dropna(axis=1, how='all').iloc[1:]
    df = df.applymap(str.strip)
    df.columns = [x.strip() for x in df.columns]
    df = df.applymap(lambda x: subs.get(x) if x in subs else x)
    return df


def prettify_table(df: pd.DataFrame):
    df = df.applymap(lambda x: str(x).strip() if x else None)
    return df
