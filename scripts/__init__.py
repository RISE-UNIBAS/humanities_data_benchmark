from pathlib import Path

from ai_client.pricing import set_pricing_file

set_pricing_file(str(Path(__file__).parent / "data" / "pricing.json"))
