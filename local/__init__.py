"""
Local (non-API) model backend registry.

To add a new backend:
1. Create local/backends/<name>.py with a class that extends LocalBackend.
2. Add an entry to LOCAL_PROVIDERS below: "provider_name": "local.backends.<name>.<ClassName>"
3. Add a test row to benchmarks_tests.csv with provider = "provider_name".
   No API key is required for local providers.
"""

import importlib

LOCAL_PROVIDERS: dict[str, str] = {
    # "provider_name": "module.path.ClassName"
    "sam3_local":            "local.backends.sam3.Sam3Backend",               # macOS / Apple Silicon
    "grounding_dino_local":  "local.backends.grounding_dino.GroundingDinoBackend",  # Windows / Linux / NVIDIA
    "doclayout_yolo_local":  "local.backends.doclayout_yolo.DocLayoutYoloBackend",  # Windows / Linux / NVIDIA
    "contour_local":         "local.backends.contour.ContourDetectionBackend",      # any OS, no GPU needed
}


def is_local_provider(provider: str) -> bool:
    """Return True if the provider is handled by a local backend (no API key needed)."""
    return provider in LOCAL_PROVIDERS


def get_backend(provider: str):
    """Instantiate and return the LocalBackend for the given provider name."""
    if provider not in LOCAL_PROVIDERS:
        raise ValueError(
            f"Unknown local provider: {provider!r}. Registered: {list(LOCAL_PROVIDERS)}"
        )
    module_path, class_name = LOCAL_PROVIDERS[provider].rsplit(".", 1)
    module = importlib.import_module(module_path)
    backend_class = getattr(module, class_name)
    return backend_class()