import json
import smtplib
import pytest
from unittest.mock import MagicMock, patch, mock_open
from IServAPI.emails import Emails  # Import the class from your module


@pytest.fixture
def mock_api():
    """Provides a cleanly mocked API core dependency for every test."""
    api = MagicMock()
    api.iserv_url = "school.iserv.de"
    api.username = "testuser"
    api._password = "securepassword"
    api._session = MagicMock()
    return api


def test_get_emails_success(mock_api):
    # 1. Arrange: Instantiate your component using the fixture
    # (Assuming your class accepts the api instance via __init__, e.g., self.api = api)
    email_client = Emails(api=mock_api)

    expected_json_data = {
        "accounts": {
            "valid": {
                "user@school.iserv.de": {
                    "mailboxes": {"mailboxes": {"inbox": {"absolutePath": "INBOX"}}}
                }
            },
            "invalid": {},
        }
    }

    mock_html_response = f"""
    <html>
    <body>
        <script id="php-data" type="application/json">{json.dumps(expected_json_data)}</script>
    </body>
    </html>
    """

    # Mock the text response property of the session's GET method
    mock_response = MagicMock()
    mock_response.text = mock_html_response
    mock_api._session.get.return_value = mock_response

    # 2. Act: Call the real method
    result = email_client.get_emails(
        path="INBOX",
        length=10,
        start=0,
        order="date",
        dir="desc",
    )

    # 3. Assert: Verify the parameters generated the exact URL requested
    expected_url = (
        "https://school.iserv.de/iserv/mail/api/message/list"
        "?path=INBOX&length=10&start=0&order%5Bcolumn%5D=date&order%5Bdir%5D=desc"
    )
    mock_api._session.get.assert_called_once_with(expected_url)

    # Verify the dictionary processing worked exactly as expected
    assert result == expected_json_data
    assert "user@school.iserv.de" in result["accounts"]["valid"]


def test_send_email_invalid_attachments_type(mock_api):
    """Verifies a TypeError is thrown immediately if attachments isn't a list."""
    emails_module = Emails(api=mock_api)

    # Act & Assert: attachments should be a list, pass a string instead
    with pytest.raises(TypeError) as exc_info:
        emails_module.send_email(
            receiver_email="target@example.com",
            subject="Test",
            body="Hello",
            attachments="not_a_list.txt",  # Invalid type trigger
        )

    assert "Attachments must be list!" in str(exc_info.value)


@patch("smtplib.SMTP_SSL")
def test_send_email_success_with_attachments(mock_smtp_ssl, mock_api, tmp_path):
    """Verifies SMTP pipeline initialization, file reads, and email transmission."""
    emails_module = Emails(api=mock_api)

    # Arrange: Create a temporary file to mock out the file system reading
    dummy_file = tmp_path / "document.pdf"
    dummy_file.write_bytes(b"dummy pdf contents")

    # Set up the context manager mock sequence for smtplib.SMTP_SSL
    mock_server_instance = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server_instance

    # Act
    emails_module.send_email(
        receiver_email="target@example.com",
        subject="Invoice",
        body="See attached.",
        attachments=[str(dummy_file)],
    )

    # Assert: Ensure it logs into the SMTP server using the client's credentials
    mock_smtp_ssl.assert_called_once_with("school.iserv.de", 465)
    mock_server_instance.login.assert_called_once_with("testuser", "securepassword")

    # Assert: Check if sendmail was triggered with proper from/to addresses
    mock_server_instance.sendmail.assert_called_once()
    args, kwargs = mock_server_instance.sendmail.call_args
    assert args[0] == "testuser@school.iserv.de"
    assert args[1] == "target@example.com"
    assert "See attached." in args[2]  # Inspect payload block text


@patch("smtplib.SMTP_SSL")
def test_send_email_smtp_exception(mock_smtp_ssl, mock_api):
    """Verifies that inner SMTP stack failures are caught and cleanly raised up."""
    emails_module = Emails(api=mock_api)

    # Arrange: Force the server login step to hit an authenticating failure exception
    mock_server_instance = MagicMock()
    mock_server_instance.login.side_effect = smtplib.SMTPAuthenticationError(
        535, "Authentication failed"
    )
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server_instance

    # Act & Assert
    with pytest.raises(smtplib.SMTPException):
        emails_module.send_email(
            receiver_email="target@example.com", subject="Fail Test", body="Boom"
        )


def _json_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


MAIL_API = "https://school.iserv.de/iserv/mail/api/v2/account/testuser@school.iserv.de"


def _client(mock_api):
    """Emails client with the mail account already resolved (no lookup request)."""
    client = Emails(api=mock_api)
    client._mail_account = "testuser@school.iserv.de"
    return client


def test_get_mail_account_from_mail_app(mock_api):
    response = MagicMock()
    response.text = (
        '<script id="php-data" type="application/json">'
        + json.dumps({"accounts": {"valid": {"john.doe@example.com": {}}, "invalid": {}}})
        + "</script>"
    )
    mock_api._session.get.return_value = response
    client = Emails(api=mock_api)

    assert client.get_mail_account() == "john.doe@example.com"
    assert client.get_mail_account() == "john.doe@example.com"
    mock_api._session.get.assert_called_once()  # cached


def test_get_mail_account_fallback(mock_api):
    response = MagicMock()
    response.text = "<html></html>"
    mock_api._session.get.return_value = response

    assert Emails(api=mock_api).get_mail_account() == "testuser@school.iserv.de"


def test_mailbox_id():
    assert Emails.mailbox_id("INBOX") == "SU5CT1g"
    assert Emails.mailbox_id("INBOX/Archiv") == "SU5CT1gvQXJjaGl2"


def test_get_mailboxes(mock_api):
    mock_api._session.get.return_value = _json_response({"mailboxes": {}})

    result = _client(mock_api).get_mailboxes()

    mock_api._session.get.assert_called_once_with(f"{MAIL_API}/mailbox")
    assert result == {"mailboxes": {}}


def test_get_mailboxes_custom_account(mock_api):
    mock_api._session.get.return_value = _json_response({})

    _client(mock_api).get_mailboxes(account="john.doe@example.com")

    mock_api._session.get.assert_called_once_with(
        "https://school.iserv.de/iserv/mail/api/v2/account/john.doe@example.com/mailbox"
    )


def test_get_messages(mock_api):
    data = {"items": [{"id": {"uid": 1}}], "total": 1, "offset": 0}
    mock_api._session.get.return_value = _json_response(data)

    result = _client(mock_api).get_messages(limit=10)

    mock_api._session.get.assert_called_once_with(
        f"{MAIL_API}/message",
        params={
            "mailbox[]": "SU5CT1g",
            "limit": 10,
            "offset": 0,
            "sort": "date",
            "order": "desc",
        },
    )
    assert result == data


def test_get_messages_search_sets_search_fields(mock_api):
    mock_api._session.get.return_value = _json_response({"items": []})

    _client(mock_api).get_messages(query="invoice")

    params = mock_api._session.get.call_args.kwargs["params"]
    assert params["q"] == "invoice"
    assert params["query_search_fields[]"] == ["subject", "from", "to"]


def test_get_message(mock_api):
    data = {"envelope": {"subject": "Hi"}, "content": {"plain": []}, "attachments": []}
    mock_api._session.get.return_value = _json_response(data)

    result = _client(mock_api).get_message(42, path="INBOX")

    mock_api._session.get.assert_called_once_with(f"{MAIL_API}/mailbox/SU5CT1g/message/42")
    assert result == data


def test_get_mail_folders_is_deprecated(mock_api):
    mock_api._session.get.return_value = _json_response({"mailboxes": {}})

    with pytest.warns(DeprecationWarning):
        result = _client(mock_api).get_mail_folders()

    mock_api._session.get.assert_called_once_with(f"{MAIL_API}/mailbox")
    assert result == {"mailboxes": {}}


def test_get_messages_single_search_field(mock_api):
    mock_api._session.get.return_value = _json_response({"items": []})

    _client(mock_api).get_messages(query="invoice", search_fields="subject")

    params = mock_api._session.get.call_args.kwargs["params"]
    assert params["query_search_fields[]"] == ["subject"]


def test_get_email_info_is_deprecated(mock_api):
    mock_api._session.get.return_value = _json_response({"items": [], "total": 3})

    with pytest.warns(DeprecationWarning):
        result = _client(mock_api).get_email_info()

    assert mock_api._session.get.call_args.args[0] == f"{MAIL_API}/message"
    assert result["total"] == 3
