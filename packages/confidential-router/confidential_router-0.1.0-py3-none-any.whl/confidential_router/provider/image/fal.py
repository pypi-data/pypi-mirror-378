import asyncio
import fal_client
from ..utils import parse_string_args


class CRFal:
    async def __call__(self, model: str, prompt: str):
        prompt, arguments = parse_string_args(prompt)
        print(prompt, arguments)
        arguments["prompt"] = prompt
        handler = await fal_client.submit_async(
            model,
            arguments=arguments
        )
        result = await handler.get()
        return result