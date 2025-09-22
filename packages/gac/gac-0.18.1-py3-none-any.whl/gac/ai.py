"""AI provider integration for gac.

This module provides core functionality for AI provider interaction.
It consolidates all AI-related functionality including token counting and commit message generation.
"""

import logging
import time
from functools import lru_cache
from typing import Any

import aisuite as ai
import tiktoken
from halo import Halo

from gac.constants import EnvDefaults, Utility
from gac.errors import AIError

logger = logging.getLogger(__name__)


def count_tokens(content: str | list[dict[str, str]] | dict[str, Any], model: str) -> int:
    """Count tokens in content using the model's tokenizer."""
    text = extract_text_content(content)
    if not text:
        return 0

    if model.startswith("anthropic"):
        import anthropic

        try:
            client = anthropic.Anthropic()

            # Use the messages.count_tokens API for accurate counting
            model_name = model.split(":", 1)[1] if ":" in model else "claude-3-5-haiku-latest"
            response = client.messages.count_tokens(model=model_name, messages=[{"role": "user", "content": text}])

            return response.input_tokens
        except Exception:
            # Fallback to simple estimation for Anthropic models
            return len(text) // 4

    try:
        encoding = get_encoding(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        return len(text) // 4


def extract_text_content(content: str | list[dict[str, str]] | dict[str, Any]) -> str:
    """Extract text content from various input formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "\n".join(msg["content"] for msg in content if isinstance(msg, dict) and "content" in msg)
    elif isinstance(content, dict) and "content" in content:
        return content["content"]
    return ""


@lru_cache(maxsize=1)
def get_encoding(model: str) -> tiktoken.Encoding:
    """Get the appropriate encoding for a given model."""
    model_name = model.split(":")[-1] if ":" in model else model
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding(Utility.DEFAULT_ENCODING)


def generate_commit_message(
    model: str,
    prompt: str | tuple[str, str],
    temperature: float = EnvDefaults.TEMPERATURE,
    max_tokens: int = EnvDefaults.MAX_OUTPUT_TOKENS,
    max_retries: int = EnvDefaults.MAX_RETRIES,
    quiet: bool = False,
) -> str:
    """Generate a commit message using aisuite.

    Args:
        model: The model to use in provider:model_name format (e.g., 'anthropic:claude-3-5-haiku-latest')
        prompt: Either a string prompt (for backward compatibility) or tuple of (system_prompt, user_prompt)
        temperature: Controls randomness (0.0-1.0), lower values are more deterministic
        max_tokens: Maximum tokens in the response
        max_retries: Number of retry attempts if generation fails
        quiet: If True, suppress progress indicators

    Returns:
        A formatted commit message string

    Raises:
        AIError: If generation fails after max_retries attempts

    Example:
        >>> model = "anthropic:claude-3-5-haiku-latest"
        >>> system_prompt, user_prompt = build_prompt("On branch main", "diff --git a/README.md b/README.md")
        >>> generate_commit_message(model, (system_prompt, user_prompt))
        'docs: Update README with installation instructions'
    """
    try:
        _, _ = model.split(":", 1)
    except ValueError as err:
        raise AIError.model_error(
            f"Invalid model format: {model}. Please use the format 'provider:model_name'."
        ) from err

    client = ai.Client()

    # Handle both old (string) and new (tuple) prompt formats
    if isinstance(prompt, tuple):
        system_prompt, user_prompt = prompt
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    else:
        # Backward compatibility: treat string as user prompt
        messages = [{"role": "user", "content": prompt}]

    if quiet:
        spinner = None
    else:
        spinner = Halo(text=f"Generating commit message with {model}...", spinner="dots")
        spinner.start()

    last_error = None

    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.debug(f"Trying with model {model} (attempt {retry_count + 1}/{max_retries})")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            message = response.choices[0].message.content if hasattr(response, "choices") else response.content

            if spinner:
                spinner.succeed(f"Generated commit message with {model}")

            return message

        except Exception as e:
            last_error = e
            retry_count += 1

            if retry_count == max_retries:
                logger.warning(f"Error generating commit message: {e}. Giving up.")
                break

            wait_time = 2**retry_count
            logger.warning(f"Error generating commit message: {e}. Retrying in {wait_time}s...")
            if spinner:
                for i in range(wait_time, 0, -1):
                    spinner.text = f"Retry {retry_count}/{max_retries} in {i}s..."
                    time.sleep(1)
            else:
                time.sleep(wait_time)
    if spinner:
        spinner.fail("Failed to generate commit message")

    error_str = str(last_error).lower()

    if "api key" in error_str or "unauthorized" in error_str or "authentication" in error_str:
        error_type = "authentication"
    elif "timeout" in error_str:
        error_type = "timeout"
    elif "rate limit" in error_str or "too many requests" in error_str:
        error_type = "rate_limit"
    elif "connect" in error_str or "network" in error_str:
        error_type = "connection"
    elif "model" in error_str or "not found" in error_str:
        error_type = "model"
    else:
        error_type = "unknown"

    raise AIError(
        f"Failed to generate commit message after {max_retries} attempts: {last_error}", error_type=error_type
    )
