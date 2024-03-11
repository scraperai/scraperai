from io import StringIO

import pandas as pd


def markdown_to_pandas(text: str, subs: dict[str, str]) -> pd.DataFrame:
    df = pd.read_csv(StringIO(text), sep='|', index_col=1).dropna(axis=1, how='all').iloc[1:]
    df = df.applymap(str.strip)
    df.columns = [x.strip() for x in df.columns]
    df = df.applymap(lambda x: subs.get(x) if x in subs else x)
    return df


def prettify_table(df: pd.DataFrame):
    df = df.applymap(lambda x: str(x).strip() if x else None)
    return df
