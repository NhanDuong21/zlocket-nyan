"""In-memory adapters used by dry-run and automated tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock

from .models import AccountCredentials, AppCheckToken, AuthSession, FriendRequestResult, Profile


@dataclass(slots=True)
class MockAccount:
    user_id: str
    credentials: AccountCredentials
    profile: Profile | None = None


@dataclass(slots=True)
class MockState:
    accounts_by_email: dict[str, MockAccount] = field(default_factory=dict)
    requests: list[FriendRequestResult] = field(default_factory=list)
    lock: RLock = field(default_factory=RLock)


class MockAppCheckProvider:
    def get_token(self) -> AppCheckToken:
        return AppCheckToken(
            value="mock-app-check-token-not-valid-outside-tests",
            provider="mock",
        )


class MockLocketApiAdapter:
    def __init__(self, state: MockState) -> None:
        self._state = state

    def create_account(
        self,
        credentials: AccountCredentials,
        app_check: AppCheckToken,
    ) -> str:
        self._require_mock_token(app_check)
        with self._state.lock:
            if credentials.email in self._state.accounts_by_email:
                raise ValueError(f"mock account already exists: {credentials.email}")
            user_id = f"mock_uid_{len(self._state.accounts_by_email) + 1:04d}"
            self._state.accounts_by_email[credentials.email] = MockAccount(
                user_id=user_id,
                credentials=credentials,
            )
            return user_id

    def finalize_profile(
        self,
        session: AuthSession,
        profile: Profile,
        app_check: AppCheckToken,
    ) -> None:
        self._require_mock_token(app_check)
        with self._state.lock:
            account = self._find_by_user_id(session.user_id)
            if profile.user_id != session.user_id:
                raise ValueError("profile user id does not match authenticated user")
            account.profile = profile

    def send_friend_request(
        self,
        session: AuthSession,
        target_uid: str,
        app_check: AppCheckToken,
    ) -> FriendRequestResult:
        self._require_mock_token(app_check)
        with self._state.lock:
            account = self._find_by_user_id(session.user_id)
            if account.profile is None:
                raise ValueError("profile must be finalized before sending a request")
            result = FriendRequestResult(
                request_id=f"mock_request_{len(self._state.requests) + 1:06d}",
                sender_uid=session.user_id,
                target_uid=target_uid,
                accepted=True,
            )
            self._state.requests.append(result)
            return result

    def _find_by_user_id(self, user_id: str) -> MockAccount:
        for account in self._state.accounts_by_email.values():
            if account.user_id == user_id:
                return account
        raise ValueError(f"unknown mock user: {user_id}")

    @staticmethod
    def _require_mock_token(app_check: AppCheckToken) -> None:
        if app_check.provider != "mock":
            raise ValueError("mock adapter only accepts mock App Check tokens")


class MockAuthAdapter:
    def __init__(self, state: MockState) -> None:
        self._state = state

    def sign_in(
        self,
        credentials: AccountCredentials,
        app_check: AppCheckToken,
    ) -> AuthSession:
        if app_check.provider != "mock":
            raise ValueError("mock auth only accepts mock App Check tokens")
        with self._state.lock:
            account = self._state.accounts_by_email.get(credentials.email)
            if account is None or account.credentials.password != credentials.password:
                raise ValueError("invalid mock credentials")
            return AuthSession(
                user_id=account.user_id,
                id_token=f"mock-id-token::{account.user_id}",
                refresh_token=f"mock-refresh-token::{account.user_id}",
            )
