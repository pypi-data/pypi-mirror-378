from __future__ import annotations

from typing import Any, List, Optional

from .core import AzureAIError


class LanguageService:
    def __init__(self, *, endpoint: Optional[str], key: Optional[str], client: Optional[Any] = None) -> None:
        self._endpoint = endpoint
        self._key = key
        self._client: Optional[Any] = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._endpoint or not self._key:
            raise AzureAIError(
                "Language credentials are missing.",
                hint="Provide endpoint/key to AzureAI(..., language_endpoint=..., language_key=...) or global endpoint/key.",
            )
        try:
            from azure.ai.textanalytics import TextAnalyticsClient
            from azure.core.credentials import AzureKeyCredential
        except Exception as ex:  # pragma: no cover - import error path
            raise AzureAIError(
                "Azure Text Analytics SDK is not installed.",
                hint="Run: pip install azure-ai-textanalytics",
            ) from ex

        self._client = TextAnalyticsClient(self._endpoint, AzureKeyCredential(self._key))
        return self._client

    @staticmethod
    def _format_summary(sentences: List[str]) -> str:
        if not sentences:
            return "No summary available."
        text = " ".join(s.strip() for s in sentences if s and isinstance(s, str))
        if not text:
            return "No summary available."
        return f"Summary: {text}"

    @staticmethod
    def _format_sentiment(result: Any) -> str:
        if not result:
            return "Sentiment: Unknown"
        try:
            doc = result[0]
            overall = getattr(doc, "sentiment", None) or "unknown"
            conf = getattr(doc, "confidence_scores", None)
            if conf:
                pos = getattr(conf, "positive", 0.0)
                neu = getattr(conf, "neutral", 0.0)
                neg = getattr(conf, "negative", 0.0)
                return f"Sentiment: {overall.title()} (P:{pos:.2f} N:{neg:.2f} U:{neu:.2f})"
            return f"Sentiment: {overall.title()}"
        except Exception:
            return "Sentiment: Unknown"

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Summarize long text into a few sentences using Extractive Summarization."""
        client = self._get_client()
        if not text or not isinstance(text, str):
            raise AzureAIError("Please provide non-empty text to summarize.")

        try:
            # Use Actions API for extractive summarization. If the SDK symbol isn't available
            # (e.g., offline demo with injected client), use a lightweight stub.
            try:
                from azure.ai.textanalytics import ExtractSummaryAction  # type: ignore
                actions = [ExtractSummaryAction(max_sentence_count=max_sentences)]
            except Exception:
                class ExtractSummaryAction:  # fallback for demo/mocked clients
                    def __init__(self, max_sentence_count: int):
                        self.max_sentence_count = max_sentence_count

                actions = [ExtractSummaryAction(max_sentence_count=max_sentences)]

            try:
                poller = client.begin_analyze_actions(documents=[text], actions=actions)
                result_pages = list(poller.result())
                sentences: List[str] = []
                for page in result_pages:
                    for action_result in page:
                        if action_result.kind == "ExtractSummary":
                            if action_result.is_error:
                                raise AzureAIError("Summarization failed.", hint=action_result.error.message)
                            for s in action_result.sentences:
                                sentences.append(getattr(s, "text", ""))
                if sentences:
                    return self._format_summary(sentences[:max_sentences])
            except Exception as ex_action:
                # Fallback: use key phrase extraction to build a concise pseudo-summary
                try:
                    kp_result = client.extract_key_phrases([text])
                    phrases = list(getattr(kp_result[0], "key_phrases", []) or [])
                    if phrases:
                        top = ", ".join(phrases[: max(3, max_sentences * 3)])
                        return f"Summary (key phrases): {top}"
                except Exception:
                    # If fallback also fails, bubble up the original action error
                    raise ex_action
            # If both paths did not return, provide a neutral message
            return "No summary available."
        except AzureAIError:
            raise
        except Exception as ex:
            raise AzureAIError(
                "Language summarization failed.",
                hint=str(ex) or "Ensure your Text Analytics resource supports extractive summarization.",
            ) from ex

    def sentiment(self, text: str) -> str:
        """Analyze sentiment of the given text and return a concise summary."""
        client = self._get_client()
        if not text or not isinstance(text, str):
            raise AzureAIError("Please provide non-empty text for sentiment analysis.")

        try:
            result = client.analyze_sentiment([text])
            return self._format_sentiment(result)
        except Exception as ex:
            raise AzureAIError(
                "Language sentiment analysis failed.",
                hint=str(ex) or "Check your endpoint/key and API version.",
            ) from ex
