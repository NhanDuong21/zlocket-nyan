from __future__ import annotations

import unittest

from zlocket.config import RunConfig
from zlocket.mock import MockAppCheckProvider, MockAuthAdapter, MockLocketApiAdapter, MockState
from zlocket.workflow import WorkflowRunner


class WorkflowTests(unittest.TestCase):
    def test_bounded_workflow_counts_every_simulated_action(self) -> None:
        state = MockState()
        config = RunConfig(accounts=2, threads=2, repeat=3, target_uid="owned_test_uid")
        runner = WorkflowRunner(
            config=config,
            app_check_provider=MockAppCheckProvider(),
            auth=MockAuthAdapter(state),
            api=MockLocketApiAdapter(state),
        )

        summary = runner.run()

        self.assertEqual(summary.accounts_created, 2)
        self.assertEqual(summary.profiles_finalized, 2)
        self.assertEqual(summary.requests_attempted, 6)
        self.assertEqual(summary.requests_accepted, 6)
        self.assertEqual(len(state.requests), 6)
        self.assertTrue(all(item.target_uid == "owned_test_uid" for item in state.requests))

    def test_historical_repeat_count_is_offline_and_bounded(self) -> None:
        state = MockState()
        config = RunConfig(accounts=1, threads=1, repeat=51)
        summary = WorkflowRunner(
            config=config,
            app_check_provider=MockAppCheckProvider(),
            auth=MockAuthAdapter(state),
            api=MockLocketApiAdapter(state),
        ).run()

        self.assertEqual(summary.requests_attempted, 51)
        self.assertEqual(len(state.requests), 51)

    def test_invalid_limits_are_rejected(self) -> None:
        for kwargs in ({"accounts": 0}, {"threads": 0}, {"repeat": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                RunConfig(**kwargs)


if __name__ == "__main__":
    unittest.main()
