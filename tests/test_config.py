import pytest
from config import get_config

def test_config_has_required_keys():
    config = get_config()
    assert config.api.binance_us_api_key is not None, "Missing API_KEY"
    assert config.api.binance_us_base_url is not None, "Missing DATA_SOURCE"