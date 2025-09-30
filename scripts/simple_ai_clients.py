"""Simple AI API client for OpenAI, GenAI, Anthropic, and Mistral AI."""
import base64
import logging
from datetime import datetime
import time
import json

from google import genai
from google.genai.types import GenerateContentConfig, Part
from openai import OpenAI
from anthropic import Anthropic
from mistralai import Mistral


class AiApiClient:
    """Simple AI API client for OpenAI, GenAI, and Anthropic."""

    SUPPORTED_APIS = ['openai',
                      'genai',
                      'anthropic',
                      'mistral']

    api_client = None
    genai_client = None
    image_resources = []
    dataclass = None

    init_time = None
    end_time = None

    def __init__(self, api, api_key, gpt_role_description=None, dataclass=None, temperature=0.5):
        if api not in self.SUPPORTED_APIS:
            raise ValueError('Unsupported API')

        self.init_time = time.time()
        self.api = api
        self.api_key = api_key
        self.gpt_role_description = gpt_role_description
        if self.gpt_role_description is None:
            self.gpt_role_description = "A useful assistant that can help you with a variety of tasks."
        self.dataclass = dataclass
        self.temperature = temperature

        self.init_client()

    def init_client(self):
        """Initialize the AI client."""
        if self.api == 'openai':
            self.api_client = OpenAI(
                api_key=self.api_key,
            )

        if self.api == 'genai':
            self.genai_client = genai.Client(api_key=self.api_key)

        if self.api == 'anthropic':
            self.api_client = Anthropic(
                api_key=self.api_key,
                timeout=300.0,  # 5 minutes timeout instead of default
            )

        if self.api == 'mistral':
            self.api_client = Mistral(
                api_key=self.api_key
            )

    @property
    def elapsed_time(self):
        """Return the elapsed time since the client was initialized."""
        if self.end_time is None:
            return time.time() - self.init_time
        return self.end_time - self.init_time

    def end_client(self):
        """End the client session."""
        self.api_client = None
        self.genai_client = None
        self.end_time = time.time()

    def add_image_resource(self, path):
        """Add an image resource to the client"""
        self.image_resources.append(path)

    def clear_image_resources(self):
        """Clear the image resources"""
        self.image_resources = []

    def prompt(self, model, prompt):
        """Prompt the AI model with a given prompt."""
        prompt_start = time.time()
        answer = None

        if self.api == 'openai':
            if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano", "o3"]:
                self.temperature = 1
            workload_json = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ]
                },
                {
                    "role": "system",
                    "content": self.gpt_role_description
                }
            ]

            for img_path in self.image_resources:
                with open(img_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

                workload_json[0]['content'].append(
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                )

            kwargs = {
                "messages": workload_json,
                "model": model,
                "temperature": self.temperature
            }
            if self.dataclass:
                kwargs["response_format"] = self.dataclass

            chat_completion = self.api_client.beta.chat.completions.parse(**kwargs)
            answer = chat_completion

        if self.api == 'genai':
            contents = [prompt]
            for img_path in self.image_resources:
                with open(img_path, 'rb') as f:
                    image_data = f.read()
                image_part = Part(
                    inline_data={
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(image_data).decode('utf-8')
                    }
                )
                contents.append(image_part)

            if self.dataclass:
                response = self.genai_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=self.dataclass,
                        temperature=self.temperature,
                    ),
                )
            else:
                response = self.genai_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=GenerateContentConfig(
                        temperature=self.temperature,
                    ),
                )

            answer = response

        if self.api == 'anthropic':
            content = [{"type": "text", "text": prompt}]
            for img_path in self.image_resources:
                with open(img_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    })

            # Determine max_tokens based on model
            if model in ["claude-3-opus-20240229"]:
                max_tokens = 4096
            elif model in ["claude-3-5-sonnet-20241022"]:
                max_tokens = 8192
            else:
                max_tokens = 10000

            # Use tools for structured output, regular client otherwise
            if self.dataclass:
                # Convert Pydantic model to JSON schema
                json_schema = self.dataclass.model_json_schema()

                # Define tool with the schema
                tools = [
                    {
                        "name": "extract_structured_data",
                        "description": "Extract structured data according to the provided schema",
                        "input_schema": json_schema,
                    }
                ]

                try:
                    # Call Anthropic with tool_choice to enforce structured output
                    message = self.api_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        tools=tools,
                        tool_choice={"type": "tool", "name": "extract_structured_data"},
                        messages=[{
                            "role": "user",
                            "content": content,
                        }],
                        timeout=300.0,
                    )
                    logging.info(f"Anthropic structured output successful")
                except Exception as e:
                    logging.warning(f"Anthropic structured output failed, trying without data schema: {e}")
                    # Fallback to regular API call
                    message = self.api_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        messages=[{
                            "role": "user",
                            "content": content,
                        }],
                        timeout=300.0,
                    )
                    # Mark as fallback for special handling in create_answer
                    message._is_fallback = True
            else:
                message = self.api_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{
                        "role": "user",
                        "content": content,
                    }],
                    timeout=300.0,
                )
            answer = message

        if self.api == 'mistral':
            content = [{"type": "text", "text": prompt}]
            for img_path in self.image_resources:
                with open(img_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    data_uri = f"data:image/jpeg;base64,{base64_image}"
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri
                        }
                    })

            kwargs = {
                "messages": [{
                    "role": "user",
                    "content": content,
                }],
                "model": model,
            }
            logging.info(self.dataclass)
            if self.dataclass:
                # Add schema to system message and use json_object mode
                schema_prompt = f"Return a JSON response matching this exact schema: {self.dataclass.model_json_schema()}"

                # Add schema instruction to the first message
                messages = kwargs["messages"].copy()
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] = messages[0]["content"] + "\n\n" + schema_prompt
                else:
                    messages.insert(0, {"role": "system", "content": schema_prompt})

                message = self.api_client.chat.complete(
                    messages=messages,
                    model=kwargs["model"],
                    response_format={"type": "json_object"}
                )
            else:
                # Use regular chat.complete() for unstructured output
                message = self.api_client.chat.complete(**kwargs)
            answer = message

        end_time = time.time()
        elapsed_time = end_time - prompt_start
        return self.create_answer(answer, elapsed_time, model)

    def create_answer(self, response, elapsed_time, model):
        """Create the response object."""
        answer = {
            'provider': self.api,
            'model': model,
            'test_time': elapsed_time,
            'execution_time': datetime.now().isoformat(),
            'response_text': "",
            'raw': response,
            'usage': {},
            'scores': {},
        }

        # Extract token usage from response
        if self.api == 'openai':
            # Extract usage: CompletionUsage(completion_tokens=2166, prompt_tokens=2333, total_tokens=4499,...)
            if hasattr(response, 'usage') and response.usage:
                answer['usage'] = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                }

            if self.dataclass:
                text = response.choices[0].message.parsed
                answer['response_text'] = text.model_dump()
            else:
                answer['response_text'] = response.choices[0].message.content
        elif self.api == 'genai':
            # Extract usage: candidates_token_count, prompt_token_count, total_token_count
            if hasattr(response, 'usage_metadata'):
                answer['usage'] = {
                    'input_tokens': response.usage_metadata.prompt_token_count,
                    'output_tokens': response.usage_metadata.candidates_token_count,
                    'total_tokens': response.usage_metadata.total_token_count,
                }

            if self.dataclass:
                # For structured output, parse JSON and validate with Pydantic
                try:
                    # Check if response has parsed attribute first
                    if hasattr(response, 'parsed') and response.parsed is not None:
                        # response.parsed should be a Pydantic model instance
                        if hasattr(response.parsed, 'model_dump'):
                            answer['response_text'] = response.parsed.model_dump()
                        else:
                            # If parsed is a dict, use it directly
                            answer['response_text'] = response.parsed
                    else:
                        # Fallback to manual JSON parsing from response.text
                        json_response = json.loads(response.text)
                        pydantic_response = self.dataclass(**json_response)
                        answer['response_text'] = pydantic_response.model_dump()
                except (json.JSONDecodeError, Exception) as e:
                    logging.warning(f"Failed to parse GenAI structured response, using raw text: {e}")
                    answer['response_text'] = response.text
            else:
                # Regular text response
                answer['response_text'] = response.text
        elif self.api == 'anthropic':
            # Extract usage: Usage(input_tokens=2285, output_tokens=2040)
            if hasattr(response, 'usage') and response.usage:
                answer['usage'] = {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens,
                }

            # Convert Message object to dict for JSON serialization
            answer['raw'] = {
                'id': response.id,
                'model': response.model,
                'role': response.role,
                'content': [{'type': block.type, 'text': block.text if hasattr(block, 'text') else None} if block.type == 'text'
                           else {'type': block.type, 'id': block.id, 'name': block.name, 'input': block.input}
                           for block in response.content],
                'stop_reason': response.stop_reason,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                } if hasattr(response, 'usage') else {}
            }

            if self.dataclass and not hasattr(response, '_is_fallback'):
                # For successful structured output via tools, parse the tool_use block
                structured = None
                for block in response.content:
                    if block.type == "tool_use" and block.name == "extract_structured_data":
                        # Validate with Pydantic and convert to dict
                        structured = self.dataclass(**block.input)
                        answer['response_text'] = structured.model_dump()
                        break

                # If no tool_use found, fall back to text content
                if structured is None:
                    logging.warning("No tool_use block found in Anthropic response, using text content")
                    answer['response_text'] = response.content[0].text if response.content else ""
            else:
                # Regular text response or fallback from tool failure
                answer['response_text'] = response.content[0].text if response.content else ""
        elif self.api == 'mistral':
            # Extract usage: UsageInfo(prompt_tokens=1873, completion_tokens=1486, total_tokens=3359)
            if hasattr(response, 'usage') and response.usage:
                answer['usage'] = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                }

            if self.dataclass:
                # For structured output, parse JSON and validate with Pydantic
                try:
                    content = response.choices[0].message.content
                    json_response = json.loads(content)
                    pydantic_response = self.dataclass(**json_response)
                    answer['response_text'] = pydantic_response.model_dump()
                except (json.JSONDecodeError, Exception) as e:
                    logging.warning(f"Failed to parse Mistral structured response, using raw text: {e}")
                    answer['response_text'] = response.choices[0].message.content
            else:
                answer['response_text'] = response.choices[0].message.content

        return answer

    def get_model_list(self):
        """Get the list of available models."""
        if self.api_client is None:
            raise ValueError('API client is not initialized.')

        if self.api == 'openai':
            return self.api_client.models.list()

        if self.api == 'genai':
            return genai.list_models()

        if self.api == 'anthropic':
            return self.api_client.models.list()

        if self.api == 'mistral':
            return self.api_client.models.list()