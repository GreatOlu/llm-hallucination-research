import os
from pathlib import Path

MODEL = "gpt-6-luna"
MAX_OUTPUT_TOKENS = 1000
client = None


def generate_response(prompt):
    global client
    if client is None:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv(Path(__file__).resolve().parents[2] / '.env')
        # Disable hidden SDK retries: each runner attempt sends at most one request.
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], max_retries=0, timeout=60.0)
    response = client.responses.create(
        model=MODEL, input=prompt, max_output_tokens=MAX_OUTPUT_TOKENS
    )
    return {
        'answer': response.output_text,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens,
        'model': response.model,
        'response_id': response.id,
        'response_status': response.status,
        'reasoning_tokens': getattr(response.usage.output_tokens_details, 'reasoning_tokens', None),
        'incomplete_reason': getattr(response.incomplete_details, 'reason', None),
    }


if __name__ == '__main__':
    print(generate_response('What is the capital of France?'))
