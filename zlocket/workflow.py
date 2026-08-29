"""Bounded orchestration for account, profile, and request simulations."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from time import monotonic
from typing import Callable

from .config import RunConfig
from .contracts import AppCheckProvider, AuthAdapter, LocketApiAdapter
from .models import AccountCredentials, AccountRunResult, AppCheckToken, Profile, RunSummary

EventSink = Callable[[str], None]


class WorkflowRunner:
    def __init__(
        self,
        config: RunConfig,
        app_check_provider: AppCheckProvider,
        auth: AuthAdapter,
        api: LocketApiAdapter,
        event_sink: EventSink | None = None,
    ) -> None:
        self._config = config
        self._app_check_provider = app_check_provider
        self._auth = auth
        self._api = api
        self._event = event_sink or (lambda _message: None)

    def run(self) -> RunSummary:
        started = monotonic()
        app_check = self._app_check_provider.get_token()
        self._event(f"App Check provider: {app_check.provider}")

        workers = min(self._config.threads, self._config.accounts)
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="zlocket-mock") as pool:
            results = list(
                pool.map(
                    lambda index: self._run_account(index, app_check),
                    range(1, self._config.accounts + 1),
                )
            )

        return RunSummary(
            environment=self._config.environment,
            accounts_requested=self._config.accounts,
            accounts_created=sum(result.account_created for result in results),
            profiles_finalized=sum(result.profile_finalized for result in results),
            requests_attempted=sum(result.requests_attempted for result in results),
            requests_accepted=sum(result.requests_accepted for result in results),
            duration_ms=round((monotonic() - started) * 1_000),
        )

    def _run_account(
        self,
        account_index: int,
        app_check: AppCheckToken,
    ) -> AccountRunResult:
        credentials = self._credentials_for(account_index)
        user_id = self._api.create_account(credentials, app_check)
        self._event(f"[account {account_index}] created {credentials.email}")

        session = self._auth.sign_in(credentials, app_check)
        profile = Profile(
            user_id=user_id,
            username=f"dryrun_{self._config.seed}_{account_index:04d}",
            first_name="zLocket",
            last_name="Dry Run",
        )
        self._api.finalize_profile(session, profile, app_check)
        self._event(f"[account {account_index}] finalized {profile.username}")

        accepted = 0
        for request_number in range(1, self._config.repeat + 1):
            result = self._api.send_friend_request(
                session,
                self._config.target_uid,
                app_check,
            )
            accepted += int(result.accepted)
            self._event(
                f"[account {account_index}] request {request_number}/{self._config.repeat} "
                f"-> {self._config.target_uid} ({result.request_id})"
            )

        return AccountRunResult(
            account_index=account_index,
            account_created=True,
            profile_finalized=True,
            requests_attempted=self._config.repeat,
            requests_accepted=accepted,
        )

    def _credentials_for(self, account_index: int) -> AccountCredentials:
        return AccountCredentials(
            email=f"dryrun+{self._config.seed}-{account_index:04d}@example.invalid",
            password=f"MockOnly-{self._config.seed}-{account_index:04d}!",
        )
