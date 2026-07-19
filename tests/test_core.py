import os
import logging
from unittest.mock import MagicMock, patch
import pytest
from IServAPI.core import Core


@pytest.fixture
def mock_auth_client():
    """Provides a mocked AuthClient instance with dummy session data."""
    with patch("IServAPI.core.AuthClient") as mock_cls:
        mock_instance = MagicMock()
        mock_instance._session = "mock_session"
        mock_instance._IServSAT = "mock_sat"
        mock_instance._IServSATId = "mock_sat_id"
        mock_instance._IServSession = "mock_iserv_session"
        mock_cls.return_value = mock_instance
        yield mock_cls


def test_core_initialization(mock_auth_client):
    """Verifies that Core correctly forwards credentials and assigns session properties."""
    username = "testuser"
    password = "secretpassword"
    iserv_url = "school.iserv.de"

    core_instance = Core(username, password, iserv_url)

    # Verify AuthClient was instantiated with the correct arguments
    mock_auth_client.assert_called_once_with(username, password, iserv_url)

    # Verify Core instance properties match what AuthClient exposed
    assert core_instance.username == username
    assert core_instance._password == password
    assert core_instance.iserv_url == iserv_url
    assert core_instance._session == "mock_session"
    assert core_instance._IServSAT == "mock_sat"
    assert core_instance._IServSATId == "mock_sat_id"
    assert core_instance._IServSession == "mock_iserv_session"
    assert core_instance._Core__DAVclient is None


def test_setup_logging(tmp_path):
    """Verifies that logging configures handlers correctly and creates a file."""
    # Use pytest's built-in tmp_path fixture to avoid cluttering workspace with log files
    log_file_path = tmp_path / "test_app.log"

    # Clear preexisting handlers to avoid overlap noise in tests
    logger = logging.getLogger()
    logger.handlers.clear()

    # Run the setup script
    Core.setup_logging(log_file=str(log_file_path))

    # Assert handlers were added properly
    assert len(logger.handlers) > 0

    # Assert specific configuration parameters from the RotatingFileHandler
    rotating_handler = [h for h in logger.handlers if hasattr(h, "maxBytes")][0]
    assert rotating_handler.maxBytes == 1024 * 1024
    assert rotating_handler.backupCount == 5

    # Check that it actually generated a file and logged the success step
    assert os.path.exists(log_file_path)
    with open(log_file_path, "r") as f:
        log_content = f.read()
        assert "Logging setup successful!" in log_content

    # Clean up handlers again so it doesn't leak into other tests running later
    logger.handlers.clear()
