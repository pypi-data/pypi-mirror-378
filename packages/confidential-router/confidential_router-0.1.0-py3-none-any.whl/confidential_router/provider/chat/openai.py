from openai import AsyncOpenAI
import os

PROVIDER_MAPPING = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "qwen": {
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "DASHSCOPE_API_KEY",
    }
}


class CROpenAI:
    def __init__(self, provider: str):
        config = PROVIDER_MAPPING[provider]
        self.client = AsyncOpenAI(
            base_url=config["base_url"], api_key=os.environ.get(config["api_key_env"])
        )

    async def __call__(
        self,
        messages: list[dict],
        model: str,
        temperature: 0.9,
        top_p=0.9,
        max_tokens=1024,
    ):
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.model_dump()