"""Shared data models for the workflow and adapters."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class AppCheckToken:
    value: str
    provider: str


@dataclass(frozen=True, slots=True)
class AccountCredentials:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class AuthSession:
    user_id: str
    id_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class Profile:
    user_id: str
    username: str
    first_name: str
    last_name: str


@dataclass(frozen=True, slots=True)
class FriendRequestResult:
    request_id: str
    sender_uid: str
    target_uid: str
    accepted: bool


@dataclass(frozen=True, slots=True)
class AccountRunResult:
    account_index: int
    account_created: bool
    profile_finalized: bool
    requests_attempted: int
    requests_accepted: int


@dataclass(frozen=True, slots=True)
class RunSummary:
    environment: str
    accounts_requested: int
    accounts_created: int
    profiles_finalized: int
    requests_attempted: int
    requests_accepted: int
    duration_ms: int

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)
