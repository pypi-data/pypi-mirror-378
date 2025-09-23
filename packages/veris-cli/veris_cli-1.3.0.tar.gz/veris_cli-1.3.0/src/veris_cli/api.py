"""API client for the Veris CLI."""

from __future__ import annotations

import os
from typing import Any

import httpx
from httpx import HTTPStatusError
from veris_cli.errors import UpstreamServiceError
from dotenv import load_dotenv


class ApiClient:
    """API client for the Veris CLI."""

    def __init__(self, base_url: str | None = None, *, timeout: float = 30.0):
        """Initialize API client.

        This ensures .env file is loaded and validates API key is present.
        """
        # Try to load .env file if VERIS_API_KEY is not already in environment
        if not os.environ.get("VERIS_API_KEY"):
            load_dotenv()

        self.base_url = base_url or os.environ.get(
            "VERIS_API_URL", "https://simulator.dev.api.veris.ai"
        )

        # Read API key from environment variable
        api_key = os.environ.get("VERIS_API_KEY")

        # Validate API key
        if api_key is None:
            raise ValueError(
                "VERIS_API_KEY environment variable is not set. "
                "Please set it in your environment or create a .env file with VERIS_API_KEY=your-key-here"
            )

        if not api_key.strip():
            raise ValueError(
                "VERIS_API_KEY environment variable is empty. Please provide a valid API key."
            )

        default_headers: dict[str, str] = {"X-API-Key": api_key}

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=default_headers,
        )

    # Internal request helper to standardize error handling
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        user_message: str | None = None,
    ) -> httpx.Response:
        try:
            response = self._client.request(method, path, json=json, params=params, headers=headers)
            response.raise_for_status()
            return response
        except HTTPStatusError as exc:
            raise UpstreamServiceError.from_httpx_error(
                exc,
                endpoint=f"{method} {path}",
                user_message=user_message or "The upstream service returned an error.",
            ) from exc

    # Scenario generation (V2)
    def start_scenario_generation(self, payload: dict[str, Any]) -> dict[str, str]:
        """Kick off scenario generation and return generation metadata.

        Expected response: { generation_id: str, status: str, message: str }
        """
        response = self._request(
            "POST",
            "/v2/scenarios/generate",
            json=payload,
            user_message=(
                "Failed to start scenario generation. This appears to be an upstream service issue."
            ),
        )
        return response.json()

    def get_generation_status(self, generation_id: str) -> dict[str, Any]:
        """Get status for a generation job."""
        response = self._request(
            "GET",
            f"/v2/scenarios/generation/{generation_id}/status",
            user_message="Failed to fetch scenario generation status.",
        )
        return response.json()

    def get_generated_scenarios(
        self, generation_id: str, include_failed: bool = False
    ) -> dict[str, Any]:
        """Retrieve generated scenarios for a generation job."""
        params = {"include_failed": str(include_failed).lower()}
        response = self._request(
            "GET",
            f"/v2/scenarios/generation/{generation_id}/scenarios",
            params=params,
            user_message="Failed to retrieve generated scenarios.",
        )
        return response.json()

    # Simulations
    def start_simulation(self, run_id: str, payload: dict[str, Any]) -> str:
        """Start a simulation."""
        response = self._request(
            "POST",
            "/v2/simulations",
            json=payload,
            headers={"X-Run-Id": run_id},
            user_message="Failed to start a simulation. This may be an upstream issue.",
        )
        data = response.json()
        simulation_id = data.get("simulation_id") or data.get("session_id")
        if not simulation_id:
            raise ValueError("Missing simulation_id/session_id in response")
        return simulation_id

    def get_simulation_status(self, simulation_id: str) -> str:
        """Get the status of a simulation."""
        response = self._request(
            "GET",
            f"/v2/simulations/{simulation_id}/status",
            user_message="Failed to fetch simulation status.",
        )
        data = response.json()
        # Expect e.g. { status: PENDING|IN_PROGRESS|COMPLETED|FAILED }
        return data.get("status", "UNKNOWN")

    def get_simulation_logs(self, simulation_id: str) -> dict[str, Any]:
        """Get the logs of a simulation."""
        response = self._request(
            "GET",
            f"/v2/simulations/{simulation_id}/logs",
            user_message="Failed to retrieve simulation logs.",
        )
        return response.json()

    def kill_simulation(self, simulation_id: str) -> None:
        """Kill a simulation."""
        self._request(
            "POST",
            f"/v2/simulations/{simulation_id}/kill",
            user_message="Failed to kill simulation.",
        )

    # Evaluations
    def start_evaluation(self, session_id: str) -> str:
        """Start an evaluation."""
        response = self._request(
            "POST",
            "/evals/evaluate",
            json={"session_id": session_id},
            user_message="Failed to start evaluation.",
        )
        data = response.json()
        eval_id = data.get("evaluation_id") or data.get("eval_id")
        if not eval_id:
            raise ValueError("Missing eval_id/evaluation_id in response")
        return eval_id

    def get_evaluation_status(self, eval_id: str) -> str:
        """Get the status of an evaluation."""
        response = self._request(
            "GET",
            f"/evals/{eval_id}/status",
            user_message="Failed to fetch evaluation status.",
        )
        data = response.json()
        return data.get("status", "UNKNOWN")

    def get_evaluation_results(self, eval_id: str) -> dict[str, Any]:
        """Get the results of an evaluation."""
        response = self._request(
            "GET",
            f"/evals/{eval_id}",
            user_message="Failed to retrieve evaluation results.",
        )
        return response.json()

    def kill_evaluation(self, eval_id: str) -> None:
        """Kill an evaluation."""
        self._request(
            "POST",
            f"/evals/{eval_id}/kill",
            user_message="Failed to kill evaluation.",
        )
