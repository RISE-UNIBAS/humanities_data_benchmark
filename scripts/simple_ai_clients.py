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
import instructor
from instructor.exceptions import InstructorRetryException  # TODO: change to instructor.core


class CostCalculator:
    """Calculate API costs using dynamic pricing lookup with database caching and Wayback fallback."""

    @classmethod
    def calculate_cost_for_date(cls, date: str, provider: str, model: str,
                               input_tokens: int, output_tokens: int) -> float:
        """Calculate cost using pricing database with Wayback fallback."""
        try:
            from pricing_database import get_pricing_database
            from wayback_scraper import WaybackScraper

            logging.info(f"Calculating cost: {input_tokens} input tokens, {output_tokens} output tokens")

            db = get_pricing_database()

            # Try to get pricing from database
            pricing_data = db.get_pricing(date, provider, model)

            if pricing_data:
                input_price, output_price, source_url = pricing_data

                # Check if pricing requires manual intervention
                if input_price is None or output_price is None:
                    logging.error(f"Pricing for {provider}/{model} requires manual intervention - prices are None")
                    logging.error(f"Please update the pricing database with actual prices for {date}")
                    return 0.0

                input_cost = (input_tokens / 1_000_000) * input_price
                output_cost = (output_tokens / 1_000_000) * output_price
                total_cost = input_cost + output_cost
                logging.info(f"Using cached pricing for {provider}/{model}: ${input_price}/${output_price}")
                logging.info(f"Cost breakdown: ${input_cost:.6f} + ${output_cost:.6f} = ${total_cost:.6f}")
                return total_cost

            # Pricing not found - fetch from Wayback Machine
            logging.info(f"Pricing not found for {date} {provider}/{model}, fetching from Wayback Machine")
            scraper = WaybackScraper()
            scraped_data = scraper.scrape_pricing(provider, date)

            if model in scraped_data:
                input_price, output_price, source_url = scraped_data[model]

                # Save to database
                db.add_pricing(date, provider, model, input_price, output_price, source_url)

                # Check if pricing requires manual intervention
                if input_price is None or output_price is None:
                    logging.error(f"Pricing for {provider}/{model} requires manual intervention - prices are None")
                    logging.error(f"Please update the pricing database with actual prices for {date}")
                    return 0.0

                # Calculate cost
                input_cost = (input_tokens / 1_000_000) * input_price
                output_cost = (output_tokens / 1_000_000) * output_price
                logging.info(f"Scraped and cached pricing for {provider}/{model}: ${input_price}/${output_price}")
                return input_cost + output_cost

            # No pricing found at all - model wasn't in scraped data, which means scraping failed
            logging.error(f"No pricing found for {date} {provider}/{model}")
            logging.warning(f"Adding {provider}/{model} to database with None prices for manual intervention")

            # Add None entry to database for manual intervention
            from datetime import datetime
            wayback_url = f"http://web.archive.org/web/{datetime.now().strftime('%Y%m%d%H%M%S')}/https://{provider}.ai/pricing"
            db.add_pricing(date, provider, model, None, None, f"{wayback_url} (MANUAL_INTERVENTION_REQUIRED)")

            return 0.0

        except Exception as e:
            logging.error(f"Error calculating cost: {e}")
            return 0.0

    @classmethod
    def calculate_cost(cls, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on current pricing (today's date)."""
        today = datetime.now().strftime('%Y-%m-%d')
        return cls.calculate_cost_for_date(today, provider, model, input_tokens, output_tokens)

    @classmethod
    def get_pricing_info(cls, provider: str, model: str, date: str = None) -> dict:
        """Get pricing information for debugging and verification."""
        try:
            from pricing_database import get_pricing_database

            if not date:
                date = datetime.now().strftime('%Y-%m-%d')

            db = get_pricing_database()
            pricing_data = db.get_pricing(date, provider, model)

            if pricing_data:
                input_price, output_price, source_url = pricing_data
                return {
                    'provider': provider,
                    'model': model,
                    'date': date,
                    'input_price_per_1m': input_price,
                    'output_price_per_1m': output_price,
                    'source_url': source_url
                }
            else:
                return {'error': f'No pricing found for {provider}/{model} on {date}'}

        except Exception as e:
            return {'error': f'Error getting pricing info: {e}'}

    @classmethod
    def verify_model_availability(cls, provider: str, model: str, date: str = None) -> bool:
        """Check if model pricing is available for cost calculation."""
        try:
            from pricing_database import get_pricing_database

            if not date:
                date = datetime.now().strftime('%Y-%m-%d')

            db = get_pricing_database()
            pricing_data = db.get_pricing(date, provider, model)
            return pricing_data is not None

        except Exception as e:
            logging.error(f"Error verifying model availability: {e}")
            return False


class AiApiClient:
    """Simple AI API client for OpenAI, GenAI, and Anthropic."""

    SUPPORTED_APIS = ['openai',
                      'genai',
                      'anthropic',
                      'mistral']

    api_client = None
    instructor_client = None
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
        self.calculate_cost = True  # Flag to enable/disable cost calculation

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
            # Initialize instructor client for structured output
            self.instructor_client = instructor.from_anthropic(self.api_client)

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
        self.instructor_client = None
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

            # Use instructor client for structured output, regular client otherwise
            if self.dataclass:
                try:
                    message = self.instructor_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        messages=[{
                            "role": "user",
                            "content": content,
                        }],
                        response_model=self.dataclass,
                        timeout=300.0,
                        max_retries=1,  # Limit retries to avoid infinite loops
                    )
                    logging.info(f"Instructor successful: {type(message)}")
                except (InstructorRetryException, Exception) as e:
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
            'scores': {},
            'cost_info': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'estimated_cost_usd': 0.0
            }
        }

        if self.api == 'openai':
            if self.dataclass:
                text = response.choices[0].message.parsed
                answer['response_text'] = text.model_dump()
            else:
                answer['response_text'] = response.choices[0].message.content

            # Extract token usage from OpenAI response
            if hasattr(response, 'usage') and response.usage:
                answer['cost_info']['input_tokens'] = response.usage.prompt_tokens
                answer['cost_info']['output_tokens'] = response.usage.completion_tokens
                answer['cost_info']['total_tokens'] = response.usage.total_tokens
                if self.calculate_cost:
                    answer['cost_info']['estimated_cost_usd'] = CostCalculator.calculate_cost(
                        self.api, model, response.usage.prompt_tokens, response.usage.completion_tokens
                    )
        elif self.api == 'genai':
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

            # Extract token usage from GenAI response
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                answer['cost_info']['input_tokens'] = response.usage_metadata.prompt_token_count
                answer['cost_info']['output_tokens'] = response.usage_metadata.candidates_token_count
                answer['cost_info']['total_tokens'] = response.usage_metadata.total_token_count
                if self.calculate_cost:
                    answer['cost_info']['estimated_cost_usd'] = CostCalculator.calculate_cost(
                        self.api, model, response.usage_metadata.prompt_token_count,
                        response.usage_metadata.candidates_token_count
                    )
        elif self.api == 'anthropic':
            if self.dataclass and not hasattr(response, '_is_fallback'):
                # For successful structured output with instructor, the response is a Pydantic model
                answer['response_text'] = response.model_dump()
            else:
                # Regular text response or fallback from instructor failure
                answer['response_text'] = response.content[0].text

            # Extract token usage from Anthropic response
            if hasattr(response, 'usage') and response.usage:
                answer['cost_info']['input_tokens'] = response.usage.input_tokens
                answer['cost_info']['output_tokens'] = response.usage.output_tokens
                answer['cost_info']['total_tokens'] = response.usage.input_tokens + response.usage.output_tokens
                if self.calculate_cost:
                    answer['cost_info']['estimated_cost_usd'] = CostCalculator.calculate_cost(
                        self.api, model, response.usage.input_tokens, response.usage.output_tokens
                    )
        elif self.api == 'mistral':
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

            # Extract token usage from Mistral response
            if hasattr(response, 'usage') and response.usage:
                answer['cost_info']['input_tokens'] = response.usage.prompt_tokens
                answer['cost_info']['output_tokens'] = response.usage.completion_tokens
                answer['cost_info']['total_tokens'] = response.usage.total_tokens
                if self.calculate_cost:
                    answer['cost_info']['estimated_cost_usd'] = CostCalculator.calculate_cost(
                        self.api, model, response.usage.prompt_tokens, response.usage.completion_tokens
                    )

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
