"""Protocols implemented by mock and future authorized adapters."""

from __future__ import annotations

from typing import Protocol

from .models import AccountCredentials, AppCheckToken, AuthSession, FriendRequestResult, Profile


class AppCheckProvider(Protocol):
    def get_token(self) -> AppCheckToken:
        """Return an environment-scoped App Check token."""


class AuthAdapter(Protocol):
    def sign_in(
        self,
        credentials: AccountCredentials,
        app_check: AppCheckToken,
    ) -> AuthSession:
        """Authenticate an account created by the API adapter."""


class LocketApiAdapter(Protocol):
    def create_account(
        self,
        credentials: AccountCredentials,
        app_check: AppCheckToken,
    ) -> str:
        """Create an account and return its user id."""

    def finalize_profile(
        self,
        session: AuthSession,
        profile: Profile,
        app_check: AppCheckToken,
    ) -> None:
        """Finalize a newly created profile."""

    def send_friend_request(
        self,
        session: AuthSession,
        target_uid: str,
        app_check: AppCheckToken,
    ) -> FriendRequestResult:
        """Send one request in the selected environment."""
