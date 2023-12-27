import enum
from pydantic import BaseModel


class ChatModelResponse(BaseModel):
    text: str
    price: float


class OpenAIModel(enum.Enum):
    gpt4 = 'gpt-4-1106-preview'
    gpt3 = 'gpt-3.5-turbo-1106'
    vision = 'gpt-4-vision-preview'


OpenAIModelPrices = {
    OpenAIModel.gpt4: (0.01, 0.03),
    OpenAIModel.gpt3: (0.001, 0.002),
    OpenAIModel.vision: (0.01, 0.03)
}
