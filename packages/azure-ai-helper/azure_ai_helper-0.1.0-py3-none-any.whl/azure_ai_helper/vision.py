from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List, Optional

from .core import AzureAIError


class VisionService:
    def __init__(self, *, endpoint: Optional[str], key: Optional[str], client: Optional[Any] = None) -> None:
        self._endpoint = endpoint
        self._key = key
        self._client: Optional[Any] = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._endpoint or not self._key:
            raise AzureAIError(
                "Vision credentials are missing.",
                hint="Provide endpoint/key to AzureAI(..., vision_endpoint=..., vision_key=...) or global endpoint/key.",
            )
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from msrest.authentication import CognitiveServicesCredentials
        except Exception as ex:  # pragma: no cover - import error path
            raise AzureAIError(
                "Azure Computer Vision SDK is not installed.",
                hint="Run: pip install azure-cognitiveservices-vision-computervision",
            ) from ex

        self._client = ComputerVisionClient(self._endpoint, CognitiveServicesCredentials(self._key))
        return self._client

    @staticmethod
    def _is_url(value: str) -> bool:
        return value.startswith("http://") or value.startswith("https://")

    @staticmethod
    def _normalize_features(features: Optional[Iterable[str]]) -> List[Any]:
        feats = list(features or ["Tags", "Description", "Categories"])
        try:
            from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes

            mapping = {"TAGS": VisualFeatureTypes.tags, "DESCRIPTION": VisualFeatureTypes.description, "CATEGORIES": VisualFeatureTypes.categories}
            return [mapping.get(str(f).upper(), f) for f in feats]
        except Exception:
            return feats

    @staticmethod
    def _fmt_conf(val: Optional[float]) -> str:
        if val is None:
            return "?"
        return f"{val:.2f}"

    @staticmethod
    def _format_result(result: Any) -> str:
        parts: List[str] = ["Image Analysis"]

        # Caption / Description
        try:
            caps = getattr(getattr(result, "description", None), "captions", None) or []
            if caps:
                cap = caps[0]
                text = getattr(cap, "text", None) or ""
                conf = VisionService._fmt_conf(getattr(cap, "confidence", None))
                parts.append(f"- Caption: {text} (confidence: {conf})")
        except Exception:
            pass

        # Tags
        try:
            tags = getattr(result, "tags", None) or []
            tag_names = [getattr(t, "name", "") for t in tags if getattr(t, "name", None)]
            if tag_names:
                parts.append(f"- Tags: {', '.join(tag_names)}")
        except Exception:
            pass

        # Categories
        try:
            categories = getattr(result, "categories", None) or []
            cat_items = []
            for c in categories:
                name = getattr(c, "name", "")
                score = VisionService._fmt_conf(getattr(c, "score", None))
                if name:
                    cat_items.append(f"{name} ({score})")
            if cat_items:
                parts.append(f"- Categories: {', '.join(cat_items)}")
        except Exception:
            pass

        return "\n".join(parts)

    def analyze(self, image: Any, features: Optional[Iterable[str]] = None) -> str:
        """Analyze an image from file path, URL, or bytes and return a concise summary.

        Args:
            image: str path, URL, Path, bytes, or file-like.
            features: Optional visual features; defaults to Tags, Description, Categories.
        Returns:
            Human-readable summary string.
        """
        client = self._get_client()
        feats = self._normalize_features(features)

        try:
            # URL path
            if isinstance(image, str) and self._is_url(image):
                result = client.analyze_image(image, visual_features=feats)
                return self._format_result(result)

            # File path
            if isinstance(image, (str, Path)):
                p = Path(image)
                if not p.exists():
                    raise AzureAIError(f"Image file not found: {p}")
                with p.open("rb") as f:
                    result = client.analyze_image_in_stream(f, visual_features=feats)
                    return self._format_result(result)

            # Raw bytes or file-like
            if isinstance(image, (bytes, bytearray)):
                import io

                stream = io.BytesIO(image)
                result = client.analyze_image_in_stream(stream, visual_features=feats)
                return self._format_result(result)

            # File-like object
            if hasattr(image, "read"):
                result = client.analyze_image_in_stream(image, visual_features=feats)
                return self._format_result(result)

            raise AzureAIError(
                "Unsupported image input type.",
                hint="Provide a URL string, a local file path, bytes, or a file-like object.",
            )
        except AzureAIError:
            raise
        except Exception as ex:
            raise AzureAIError(
                "Vision analysis failed.",
                hint=str(ex) or "Check your endpoint/key and that the image is accessible.",
            ) from ex
