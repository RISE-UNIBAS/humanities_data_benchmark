"""Simple AI API client for OpenAI, GenAI, Anthropic, and Mistral AI."""
import base64
from dataclasses import asdict
from datetime import datetime
import time

import google.generativeai as genai
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
            genai.configure(api_key=self.api_key)

        if self.api == 'anthropic':
            self.api_client = Anthropic(
                api_key=self.api_key,
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
            model_obj = genai.GenerativeModel(model)
            images = []
            for img_path in self.image_resources:
                image_file = genai.upload_file(path=img_path)
                images.append(image_file)

            response = model_obj.generate_content([prompt] + images)
            answer = response

        if self.api == 'anthropic':
            # Anthropic supports images via base64 inline embedding
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
            if model in ["claude-3-opus-20240229"]:
                message = self.api_client.messages.create(
                    max_tokens=4096,
                    messages=[{
                        "role": "user",
                        "content": content,
                    }],
                    model=model,
                )
            elif model in ["claude-3-5-sonnet-20241022"]:
                message = self.api_client.messages.create(
                    max_tokens=8192,
                    messages=[{
                        "role": "user",
                        "content": content,
                    }],
                    model=model,
                )
            else:
                message = self.api_client.messages.create(
                    max_tokens=10000,
                    messages=[{
                        "role": "user",
                        "content": content,
                    }],
                    model=model,
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

            message = self.api_client.chat.complete(
                messages=[{
                    "role": "user",
                    "content": content,
                }],
                model=model,
            )
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
            'scores': {},
        }

        if self.api == 'openai':
            if self.dataclass:
                text = response.choices[0].message.parsed
                answer['response_text'] = asdict(text)
            else:
                answer['response_text'] = response.choices[0].message.content
        elif self.api == 'genai':
            answer['response_text'] = response.text
        elif self.api == 'anthropic':
            answer['response_text'] = response.content[0].text
        elif self.api == 'mistral':
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
