import asyncio
import random
from typing import Optional

from openai import APIError, OpenAI, RateLimitError
from pydantic import BaseModel, ValidationError

# http_client = httpx()
# test_client = OpenAI(http_client=http_client)


async def flex_processing(
    LLM_client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    output_model: Optional[BaseModel] = None,
    prompt_cache_key: Optional[str] = None,
    max_retries: int = 10,
    base_delay: float = 2.0,
    model_name: Optional[str] = "gpt-5-mini",
    **client_kwargs,
):
    """
    Wrapper for flex processing with retry and exponential backoff.
    Handles 429 'Resource Unavailable' errors gracefully.
    """
    for attempt in range(max_retries):
        try:
            request_kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "service_tier": "flex",
                "timeout": 900.0,
                **client_kwargs,
            }
            if output_model:
                request_kwargs["response_format"] = output_model
            if prompt_cache_key:
                request_kwargs["prompt_cache_key"] = prompt_cache_key

            response = LLM_client.chat.completions.parse(**request_kwargs)
            # response = self.client.chat.completions.parse(output_model)
            content = response.choices[0].message.content
            # ✅ Validate structured output if a model is provided
            if output_model is not None:
                try:
                    output_model.model_validate_json(content)
                    base_content = response.choices[0].message.parsed
                    # base_content = output_model(**content)
                    return base_content
                except ValidationError as ve:
                    # Treat invalid output as retryable
                    wait_time = base_delay * (2**attempt) + random.uniform(0, 1)
                    print(
                        f"[Flex Retry] Attempt {attempt + 1}/{max_retries} produced invalid structured output. "
                        f"Retrying in {wait_time:.2f}s... (ValidationError: {ve})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
        except (RateLimitError, APIError) as e:
            wait_time = base_delay * (2**attempt) + random.uniform(0, 1)
            print(
                f"[Flex Retry] Attempt {attempt + 1}/{max_retries} failed "
                f"with error: {type(e).__name__} - {e}. "
                f"Retrying in {wait_time:.2f}s..."
            )
            await asyncio.sleep(wait_time)

        except Exception as e:
            # Non-recoverable error: break out immediately
            raise RuntimeError(
                f"[Flex Processing] Unrecoverable error for prompt_key={prompt_cache_key}: {e}"
            )

    raise RuntimeError(
        f"[Flex Processing] Exhausted {max_retries} retries for prompt_key={prompt_cache_key}"
    )
