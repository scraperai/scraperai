import random
from pathlib import Path


with open(Path(__file__).resolve().parent / 'useragents.txt', 'r') as f:
    useragentarray = list(f.read().split('\n'))


def get_random_useragent() -> str:
    index = random.randint(0, len(useragentarray) - 1)
    return useragentarray[index]

