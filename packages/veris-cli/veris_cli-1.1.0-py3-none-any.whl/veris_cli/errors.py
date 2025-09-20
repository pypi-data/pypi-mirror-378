"""Custom error types for the Veris CLI."""

from __future__ import annotations

from dataclasses import dataclass

from httpx import HTTPStatusError


@dataclass
class UpstreamServiceError(Exception):
    """Represents a failure returned by the upstream Veris services.

    This error is designed to produce a clear, copyable message that users can
    paste to the Veris team for faster debugging. Prefer raising this instead of
    raw HTTP exceptions within the CLI.
    """

    message: str
    scenario_id: str | None = None
    run_id: str | None = None
    simulation_id: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    response_body: str | None = None

    def __str__(self) -> str:  # pragma: no cover - string formatting only
        """Return a human-friendly, copyable error message for CLI display."""
        lines: list[str] = []

        if self.response_body:
            lines.append("Response Body (for debugging):")
            lines.append(self.response_body)
        lines.append("Upstream service error while processing evaluation.")
        if self.message:
            lines.append(f"Reason: {self.message}")
        if self.status_code is not None:
            lines.append(f"HTTP Status: {self.status_code}")
        if self.endpoint:
            lines.append(f"Endpoint: {self.endpoint}")
        if self.run_id:
            lines.append(f"Run ID: {self.run_id}")
        if self.simulation_id:
            lines.append(f"Simulation ID: {self.simulation_id}")
        if self.scenario_id:
            lines.append(f"Scenario ID: {self.scenario_id}")
        lines.append(
            "Please copy this entire message and send it to the Veris team so we can investigate."
        )
        return "\n".join(lines)

    @classmethod
    def from_httpx_error(
        cls,
        exc: HTTPStatusError,
        *,
        scenario_id: str | None = None,
        run_id: str | None = None,
        simulation_id: str | None = None,
        endpoint: str | None = None,
        user_message: str | None = None,
    ) -> "UpstreamServiceError":
        """Create an UpstreamServiceError from an HTTPStatusError."""
        status_code: int | None = None
        response_body: str | None = None
        try:
            status_code = exc.response.status_code  # type: ignore[assignment]
            # Prefer text to preserve raw server message
            response_body = exc.response.text
        except Exception:
            # If the response object is missing or unreadable, ignore
            pass

        message = user_message or "The upstream service returned an error."
        return cls(
            message=message,
            scenario_id=scenario_id,
            run_id=run_id,
            simulation_id=simulation_id,
            endpoint=endpoint,
            status_code=status_code,
            response_body=response_body,
        )
