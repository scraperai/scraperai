# LLMs

ScraperAI heavily relies on Large Language Models (LLMs) to analyze webpage content and extract relevant information. 
To ensure flexibility and quality, we integrate [langchain](https://github.com/langchain-ai/langchain) as a core AI package.

## OpenAI
By default, ScraperAI utilizes the latest OpenAI's ChatGPT model (`gpt-4-turbo-2024-04-09`).

To use another OpenAI model pass its name during initialization:
```python
from scraperai import JsonOpenAI

model = JsonOpenAI(openai_api_key='sk-...', model_name='gpt-3.5-turbo')
```
You can access total USD spent using `total_cost` property.

## Custom models
ScraperAI provides flexibility to integrate any other model capable of generating JSON answers.
> Please note that although ScraperAI utilizes HTML minification, it still requires LLMs to be capable of processing substantial contexts. 
> It's recommended that the model's input size be equal to or greater than approximately 16k Byte-Pair Encoded tokens.

To implement a custom model, simply inherit from the following abstract class:

```python
from langchain_core.messages import BaseMessage
from scraperai import BaseJsonLM

class YourJsonModel(BaseJsonLM):
    def invoke(self, messages: list[BaseMessage]) -> dict:
        ...
```

Then, pass your model to the `ParserAI` during initialization:

```python
from scraperai import ParserAI

parser = ParserAI(json_lm_model=YourJsonModel(), ...)
```

We are working on extending a list of models available out of the box.

# Vision Models

Vision Models play a crucial role in ScraperAI for determining webpage types and generating descriptions of webpages.

While usage of Vision Models is recommended, it's not mandatory. 
Experiments have demonstrated the effectiveness of the Vision approach compared to using JSON Models with HTML inputs.

## OpenAI
By default, ScraperAI employs the latest OpenAI's ChatGPT model (`gpt-4-vision-preview`). 

To use another OpenAI model pass its name during initialization:
```python
from scraperai import VisionOpenAI

model = VisionOpenAI(openai_api_key='sk-...', model_name='gpt-4-1106-vision-preview')
```

You can access total USD spent using `total_cost` property.
## Custom models
ScraperAI provides flexibility to integrate any other model by extending the abstract class as follows:

```python
from langchain_core.messages import BaseMessage
from scraperai import BaseVision

class YourVisionModel(BaseVision):
    def invoke(self, messages: list[BaseMessage]) -> str:
        ...
```
Note: ScraperAI passes the image as a base64 encoded string to the `image_url` field of `HumanMessage`.
