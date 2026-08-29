"""Runtime configuration and validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunConfig:
    """A bounded run configuration for the offline mock environment."""

    environment: str = "mock"
    accounts: int = 1
    threads: int = 1
    repeat: int = 1
    target_uid: str = "test_receiver"
    seed: int = 2026

    MAX_ACCOUNTS = 100
    MAX_THREADS = 16
    MAX_REPEAT = 1_000

    def __post_init__(self) -> None:
        if self.environment != "mock":
            raise ValueError("Only the offline 'mock' environment is available")
        if not 1 <= self.accounts <= self.MAX_ACCOUNTS:
            raise ValueError(f"accounts must be between 1 and {self.MAX_ACCOUNTS}")
        if not 1 <= self.threads <= self.MAX_THREADS:
            raise ValueError(f"threads must be between 1 and {self.MAX_THREADS}")
        if not 1 <= self.repeat <= self.MAX_REPEAT:
            raise ValueError(f"repeat must be between 1 and {self.MAX_REPEAT}")
        if not self.target_uid.strip():
            raise ValueError("target_uid cannot be empty")

    @property
    def total_actions(self) -> int:
        return self.accounts * self.repeat
