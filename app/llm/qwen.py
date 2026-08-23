from openai import OpenAI, APITimeoutError, APIError
from app.exceptions.exceptions import LLMTimeoutError, LLMServiceError
from app.config import API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS


client = OpenAI(
    api_key=API_KEY,
    base_url=LLM_BASE_URL
)


def chat_with_qwen_stream(prompt: str):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=True
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    except APITimeoutError:
        raise LLMTimeoutError()
    except APIError:
        raise LLMServiceError()
    except Exception:
        raise LLMServiceError("LLM未知错误")


def chat_with_qwen(prompt: str):
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return response.choices[0].message.content

    except APITimeoutError:
        raise LLMTimeoutError()
    except APIError:
        raise LLMServiceError()
    except Exception:
        raise LLMServiceError("LLM未知错误")
