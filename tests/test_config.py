"""Tests for configuration module."""
import os
import pytest
from unittest.mock import patch, MagicMock


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_loads_from_environment(self):
        """Test that config loads from environment variables."""
        from config.settings import Config

        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
            'PAPER_MODE': 'true'
        }):
            config = Config.from_env()
            assert config.api_key == 'test_key'
            assert config.api_secret == 'test_secret'
            assert config.paper_mode is True

    def test_paper_mode_false_for_live_trading(self):
        """Test that paper_mode=false enables live trading."""
        from config.settings import Config

        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
            'PAPER_MODE': 'false'
        }):
            config = Config.from_env()
            assert config.paper_mode is False

    def test_risk_parameters_have_defaults(self):
        """Test that risk management parameters have sensible defaults."""
        from config.settings import Config

        with patch.dict(os.environ, {
            'ALPACA_API_KEY': 'test_key',
            'ALPACA_SECRET_KEY': 'test_secret',
        }, clear=False):
            config = Config.from_env()
            assert config.max_position_pct == 0.20
            assert config.daily_loss_limit_pct == 0.05
            assert config.max_order_notional == 10000
