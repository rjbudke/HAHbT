"""Tests for HAHbT button visibility rules."""

from __future__ import annotations

import unittest

from _ha_stubs import install

install()

from custom_components.hahbt.button import should_expose_log_button
from custom_components.hahbt.const import (
    STATUS_ACTIVE,
    STATUS_ARCHIVED,
    STATUS_INACTIVE,
)


class HahbtButtonTests(unittest.TestCase):
    """Cover the active-only quick-log button surface."""

    def test_log_button_exposed_for_active_habits(self) -> None:
        self.assertTrue(should_expose_log_button(STATUS_ACTIVE))

    def test_log_button_hidden_for_inactive_habits(self) -> None:
        self.assertFalse(should_expose_log_button(STATUS_INACTIVE))

    def test_log_button_hidden_for_archived_habits(self) -> None:
        self.assertFalse(should_expose_log_button(STATUS_ARCHIVED))
