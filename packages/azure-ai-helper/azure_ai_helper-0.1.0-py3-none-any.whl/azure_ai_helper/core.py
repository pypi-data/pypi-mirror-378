from __future__ import annotations
from typing import Optional


class AzureAIError(Exception):
    """User-friendly error for azure_ai_helper."""

    def __init__(self, message: str, hint: Optional[str] = None):
        self.hint = hint
        full = message if not hint else f"{message}\nHint: {hint}"
        super().__init__(full)



class AzureAI:
    """Unified entry point to Azure AI services with a clean API.

    Example:
        ai = AzureAI(endpoint="ENDPOINT", key="KEY")
        print(ai.vision.analyze("image.jpg"))
        print(ai.language.summarize("Long text..."))
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        vision_endpoint: Optional[str] = None,
        vision_key: Optional[str] = None,
        language_endpoint: Optional[str] = None,
        language_key: Optional[str] = None,
    ) -> None:
        self._endpoint = endpoint
        self._key = key

        # Lazy import to avoid circulars when importing submodules directly in tests
        from .vision import VisionService  # type: ignore
        from .language import LanguageService  # type: ignore

        self.vision = VisionService(endpoint=vision_endpoint or endpoint, key=vision_key or key)
        self.language = LanguageService(endpoint=language_endpoint or endpoint, key=language_key or key)

    # Future placeholders
    @property
    def speech(self):
        raise AzureAIError(
            "Speech service is not implemented yet.",
            hint="This placeholder will enable speech-to-text and text-to-speech in a future release.",
        )
