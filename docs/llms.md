# LLMs

ScraperAI heavily relies on Large Language Models (LLMs) to analyze webpage content and extract relevant information. 
To ensure flexibility and quality, we integrate [langchain](https://github.com/langchain-ai/langchain) as a core AI package.

By default, ScraperAI utilizes the latest OpenAI's ChatGPT model (`gpt-4-0125-preview`). 
However, users have the flexibility to integrate any other model capable of generating JSON answers.
> Please note that although ScraperAI utilizes HTML minification, it still requires LLMs to be capable of processing substantial contexts. 
> It's recommended that the model's input size be equal to or greater than approximately 16k Byte-Pair Encoded tokens.

To implement a custom model, simply inherit from the following abstract class:

```python
from langchain_core.messages import BaseMessage

class YourJsonModel(BaseJsonLM):
    def invoke(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        ...
```

Then, pass your model to the `ParserAI` during initialization:

```python
parser = ParserAI(json_lm_model=YourModel(), ...)
```

We are working on extending a list of models available out of the box.

## Vision Models

Vision Models play a crucial role in ScraperAI for determining webpage types and generating descriptions of webpages.

While usage of Vision Models is recommended, it's not mandatory. 
Experiments have demonstrated the effectiveness of the Vision approach compared to using JSON Models with HTML inputs.

By default, ScraperAI employs the latest OpenAI's ChatGPT model for vision (`gpt-4-vision-preview`). 
However, users can integrate any other model by extending the abstract class as follows:

```python
from langchain_core.messages import BaseMessage

class YourVisionModel(BaseVision):
    def invoke(self, messages: List[BaseMessage]) -> str:
        ...
```
Note: ScraperAI passes the image as a base64 encoded string to the `image_url` field of `HumanMessage`.
