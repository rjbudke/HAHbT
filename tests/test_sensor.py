"""Tests for HAHbT sensor visibility rules."""

from __future__ import annotations

import unittest

from _ha_stubs import install

install()

from custom_components.hahbt.const import STATUS_ACTIVE, STATUS_ARCHIVED, STATUS_INACTIVE
from custom_components.hahbt.sensor import should_expose_metric_entities


class HahbtSensorTests(unittest.TestCase):
    """Cover the metric entity visibility rules."""

    def test_metric_entities_exposed_for_active_habits(self) -> None:
        self.assertTrue(should_expose_metric_entities(STATUS_ACTIVE))

    def test_metric_entities_exposed_for_inactive_habits(self) -> None:
        self.assertTrue(should_expose_metric_entities(STATUS_INACTIVE))

    def test_metric_entities_hidden_for_archived_habits(self) -> None:
        self.assertFalse(should_expose_metric_entities(STATUS_ARCHIVED))
