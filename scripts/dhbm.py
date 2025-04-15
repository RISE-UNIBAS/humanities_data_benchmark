import argparse
import json
import os
import logging
from benchmark_base import Benchmark
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def get_api_key(provider, cli_api_key=None):
    """Fetch the API key from the command-line argument or environment variables."""
    if cli_api_key:
        return cli_api_key
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        raise ValueError(f"No API key found for {provider.upper()} (set via --api_key or environment variable).")
    return api_key


def run_test(test_config, api_key, date=None):
    """Execute a single test and return the response JSON."""
    benchmark_directory = os.path.join(os.getcwd(), "benchmarks", test_config["name"])

    benchmark = Benchmark(test_config, api_key, benchmark_directory, date)
    response = benchmark.ask_llm([])  # No images assumed for simplicity

    print(json.dumps(response, indent=4))
    return response


def main():
    parser = argparse.ArgumentParser(description="Run a single AI benchmark test.")
    parser.add_argument("--config", type=str, required=False,
                        help="Path to a JSON file containing the test configuration.")
    parser.add_argument("--name", type=str, help="Name of the test (folder name).")
    parser.add_argument("--provider", type=str, help="API provider (openai, genai, anthropic).")
    parser.add_argument("--model", type=str, help="Model name (e.g., gpt-4).")
    parser.add_argument("--role_description", type=str, help="Description of AI role.")
    parser.add_argument("--prompt_file", type=str, help="File name of the prompt.")
    parser.add_argument("--api_key", type=str, required=False, help="API key for the provider.")
    parser.add_argument("--date", type=str, required=False, help="Date to use for results (YYYY-MM-DD format)")

    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as f:
            test_config = json.load(f)
    else:
        if not all([args.name, args.provider, args.model, args.role_description, args.prompt_file]):
            parser.error("Either provide --config JSON file or all required arguments.")
        test_config = {
            "name": args.name,
            "provider": args.provider,
            "model": args.model,
            "role_description": args.role_description,
            "prompt_file": args.prompt_file
        }

    try:
        api_key = get_api_key(test_config["provider"], args.api_key)
        response = run_test(test_config, api_key, args.date)
    except Exception as e:
        logger.error(f"Error running test: {e}")


if __name__ == "__main__":
    main()
