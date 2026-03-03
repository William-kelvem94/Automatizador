from unittest.mock import Mock, patch

import pytest

from src.core.automation_engine import AutomationEngine


@pytest.fixture
def config_mock():
    return {
        "url": "https://example.com/login",
        "email_selector": "#email",
        "password_selector": "#password",
        "submit_selector": "#submit",
    }


def test_automation_engine_init(config_mock):
    engine = AutomationEngine(config_mock)
    assert engine.config == config_mock
    assert engine.browser is None


@patch("src.core.automation_engine.FieldDetector")
@patch("src.core.automation_engine.BrowserEngine")
def test_automation_engine_initialize(browser_mock, field_mock, config_mock):
    engine = AutomationEngine(config_mock)
    engine.initialize()
    browser_mock.assert_called_once()
    assert engine.logger is not None
