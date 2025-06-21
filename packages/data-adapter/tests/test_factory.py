import pytest
from unittest.mock import patch, MagicMock

from data_adapter import get_adapter
from data_adapter.config import ProviderSettings
from data_adapter.exceptions import ConfigurationError
from data_adapter.providers.fmp.adapter import FMPAdapter


@patch("data_adapter.factory.redis.Redis", return_value=MagicMock())
@patch("data_adapter.factory.settings")
def test_get_adapter_success(mock_settings, mock_redis):
    """
    Test that the factory returns the correct adapter instance.
    """
    mock_settings.data_providers = {"fmp": ProviderSettings(api_key="test_key")}
    adapter = get_adapter("fmp")
    assert isinstance(adapter, FMPAdapter)


@patch("data_adapter.factory.redis.Redis", return_value=MagicMock())
@patch("data_adapter.factory.settings")
def test_get_adapter_not_found(mock_settings, mock_redis):
    """
    Test that a ConfigurationError is raised for an unknown provider.
    """
    mock_settings.data_providers = {}
    with pytest.raises(ConfigurationError):
        get_adapter("unknown_provider")


@patch("data_adapter.factory.redis.Redis", return_value=MagicMock())
@patch("data_adapter.factory.settings")
def test_get_adapter_no_settings(mock_settings, mock_redis):
    """
    Test that a ConfigurationError is raised when no settings are found for a provider.
    """
    mock_settings.data_providers = {}
    with pytest.raises(ConfigurationError):
        get_adapter("fmp") 