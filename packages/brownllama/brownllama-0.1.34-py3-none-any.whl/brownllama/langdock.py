"""
Langdock API Call.

This module provides a class for generating responses, chat using the Langdock API.
"""

import requests


class Langdock:
    """A class for generating responses using the Langdock API."""

    def __init__(self, api_key: str) -> None:
        """
        Initialize the Langdock class.

        Args:
            api_key (str): The API key for accessing the Langdock API.

        """
        self.url = "https://api.langdock.com/openai/eu/v1/chat/completions"
        self.headers = {"Authorization": api_key, "Content-Type": "application/json"}

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the GenAI API.

        Args:
            prompt (str): The prompt for generating the response.

        Returns:
            The generated response.

        """
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        }

        response = requests.post(
            self.url, json=payload, headers=self.headers, timeout=60
        )

        return response.json()
