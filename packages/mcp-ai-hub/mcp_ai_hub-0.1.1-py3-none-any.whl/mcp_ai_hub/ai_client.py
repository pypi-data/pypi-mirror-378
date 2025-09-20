"""LiteLM integration wrapper for AI providers."""

import logging
from typing import Any

import litellm

from .config import AIHubConfig, ModelConfig

logger = logging.getLogger(__name__)


class AIClient:
    """Wrapper around LiteLM for unified AI provider access."""

    def __init__(self, config: AIHubConfig):
        """Initialize AI client with configuration."""
        self.config = config
        # Set LiteLM to suppress output
        litellm.suppress_debug_info = True

    def chat(self, model_name: str, inputs: str | list[dict[str, Any]]) -> str:
        """Chat with specified AI model.

        Args:
            model_name: Name of the model to use
            inputs: Chat input (string or OpenAI-format messages)

        Returns:
            AI model response as string

        Raises:
            ValueError: If model is not configured
            Exception: If API call fails
        """
        model_config = self.config.get_model_config(model_name)
        if not model_config:
            available_models = self.config.list_available_models()
            raise ValueError(
                f"Model '{model_name}' not found in configuration. "
                f"Available models: {', '.join(available_models)}"
            )

        # Convert input to messages format and apply system prompt
        messages = self._prepare_messages(inputs, model_config)

        try:
            # Get the model parameter and validate it
            litellm_model = model_config.litellm_params.get("model")
            if not litellm_model:
                raise ValueError(
                    f"Model configuration for '{model_name}' missing 'model' parameter"
                )

            # Make the API call using LiteLM (ensure non-streaming)
            litellm_params = {
                k: v for k, v in model_config.litellm_params.items() if k != "model"
            }
            litellm_params["stream"] = False  # Explicitly disable streaming

            response = litellm.completion(
                model=litellm_model, messages=messages, **litellm_params
            )

            # Extract content from response - LiteLM follows OpenAI format
            # Using getattr and exception handling for robust access
            try:
                # LiteLM response structure: response.choices[0].message.content
                choices_attr = getattr(response, "choices", None)
                choices_list: list[Any] = []
                if isinstance(choices_attr, list | tuple):
                    choices_list = list(choices_attr)
                elif isinstance(response, dict):
                    maybe_choices = response.get("choices")
                    if isinstance(maybe_choices, list | tuple):
                        choices_list = list(maybe_choices)

                if choices_list:
                    first_choice = choices_list[0]
                    message: Any
                    if isinstance(first_choice, dict):
                        message = first_choice.get("message")
                    else:
                        message = getattr(first_choice, "message", None)

                    if message:
                        if isinstance(message, dict):
                            content = message.get("content")
                        else:
                            content = getattr(message, "content", None)
                        if content:
                            return str(content)

                return ""
            except (AttributeError, IndexError, TypeError) as e:
                logger.warning("Unexpected response format from %s: %s", model_name, e)
                return ""

        except Exception as e:
            logger.error("Error calling model %s: %s", model_name, e)
            raise RuntimeError(
                f"Failed to get response from {model_name}: {str(e)}"
            ) from e

    def _prepare_messages(
        self,
        inputs: str | list[dict[str, Any]],
        model_config: ModelConfig | None = None,
    ) -> list[dict[str, Any]]:
        """Convert inputs to OpenAI messages format with system prompt support."""
        messages: list[dict[str, Any]] = []

        # Determine system prompt with precedence: model-specific > global
        system_prompt: str | None
        if model_config is not None and hasattr(model_config, "system_prompt"):
            # Use model-specific value if explicitly set (including empty string
            # to intentionally disable/override any global prompt). Only fall back
            # to global when the model-level value is None (unset).
            if model_config.system_prompt is not None:
                system_prompt = model_config.system_prompt
            else:
                system_prompt = self.config.global_system_prompt
        else:
            system_prompt = self.config.global_system_prompt

        # Add system prompt if configured
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if isinstance(inputs, str):
            # Simple string input
            messages.append({"role": "user", "content": inputs})
        elif isinstance(inputs, list):
            # Already in messages format, validate structure
            for msg in inputs:
                if (
                    not isinstance(msg, dict)
                    or "role" not in msg
                    or "content" not in msg
                ):
                    raise ValueError(
                        "Invalid message format. Each message must have 'role' and 'content' keys."
                    )
            messages.extend(inputs)
        else:
            raise ValueError(
                "Inputs must be either a string or a list of message dictionaries."
            )

        return messages

    def list_models(self) -> list[str]:
        """List all available models."""
        return self.config.list_available_models()

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        """Get information about a specific model."""
        model_config = self.config.get_model_config(model_name)
        if not model_config:
            raise ValueError(f"Model '{model_name}' not found in configuration.")

        return {
            "model_name": model_config.model_name,
            "provider_model": model_config.litellm_params.get("model"),
            "configured_params": list(model_config.litellm_params.keys()),
            "system_prompt": model_config.system_prompt,
            "global_system_prompt": self.config.global_system_prompt,
        }
