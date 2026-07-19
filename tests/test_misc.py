import json
import pytest
from unittest.mock import MagicMock
from IServAPI.misc import Misc  # Adjust this import to match your file layout


@pytest.fixture
def mock_api():
    """Provides a mocked API object with a session mock attached."""
    api = MagicMock()
    api.iserv_url = "school.iserv.de"
    api._session = MagicMock()
    return api


def test_get_conference_health(mock_api):
    """Verifies conference health correctly parses the JSON payload from the request."""
    misc = Misc(api=mock_api)

    # Setup mock response for the health endpoint
    expected_payload = {
        "load": 0.01241202976392663,
        "normalizedLoad": 2,
        "loadClassification": "green",
        "loadDescription": "Geringe Auslastung",
        "counter": {"meetings": 4, "participants": 13, "threads": 512},
    }
    mock_response = MagicMock()
    mock_response.json.return_value = expected_payload
    mock_api._session.get.return_value = mock_response

    # Execute
    result = misc.get_conference_health()

    # Assertions
    mock_api._session.get.assert_called_once_with(
        "https://school.iserv.de/iserv/videoconference/api/health"
    )
    assert result == expected_payload


def test_get_disk_space(mock_api):
    """Verifies beautifulsoup DOM extraction and JSON conversion are functioning."""
    misc = Misc(api=mock_api)

    # Mock HTML structure mirroring what the method expects
    mock_html = """
<div class="d-flex w-100" id="user-diskusage">
    <script id="user-diskusage-data" type="application/json">[{"label":"Dateien","size":"1897647930","color":"#F6D26F","sizeHuman":"1,810 MB"},{"label":"Wolke","size":"24598","color":"#66BAFF","sizeHuman":"1 MB"},{"label":"E-Mail","size":"234403529","color":"#BFCCE3","sizeHuman":"224 MB"},{"label":"Drucken","size":"147619","color":"#6E82FA","sizeHuman":"1 MB"},{"label":"Temp","size":"12288","color":"#CCCCCC","sizeHuman":"1 MB"},{"label":"Rest","size":"12910","color":"#444444","sizeHuman":"1 MB"},{"label":"Windows-Anwendungsdaten (Remote.V2)","size":"1831722574","color":"#AE4DB5","sizeHuman":"1,747 MB"},{"label":"Windows-10-Profil (Local.V6)","size":"714626313","color":"#0083FF","sizeHuman":"682 MB"}]</script>
    <div class="user-diskusage-chart-wrapper">
        <canvas id="user-diskusage-chart"></canvas>
    </div>
</div>

<script src="/iserv/assets/vendor/js/chartjs.706b80a1.js"></script>
<script src="/iserv/assets/du/js/account.deb1c000.js"></script>

    """
    mock_response = MagicMock()
    mock_response.text = mock_html
    mock_api._session.get.return_value = mock_response

    # Execute
    result = misc.get_disk_space()

    # Assertions
    mock_api._session.get.assert_called_once_with(
        "https://school.iserv.de/iserv/du/account"
    )
    assert result == [
        {
            "label": "Dateien",
            "size": "1897647930",
            "color": "#F6D26F",
            "sizeHuman": "1,810 MB",
        },
        {"label": "Wolke", "size": "24598", "color": "#66BAFF", "sizeHuman": "1 MB"},
        {
            "label": "E-Mail",
            "size": "234403529",
            "color": "#BFCCE3",
            "sizeHuman": "224 MB",
        },
        {"label": "Drucken", "size": "147619", "color": "#6E82FA", "sizeHuman": "1 MB"},
        {"label": "Temp", "size": "12288", "color": "#CCCCCC", "sizeHuman": "1 MB"},
        {"label": "Rest", "size": "12910", "color": "#444444", "sizeHuman": "1 MB"},
        {
            "label": "Windows-Anwendungsdaten (Remote.V2)",
            "size": "1831722574",
            "color": "#AE4DB5",
            "sizeHuman": "1,747 MB",
        },
        {
            "label": "Windows-10-Profil (Local.V6)",
            "size": "714626313",
            "color": "#0083FF",
            "sizeHuman": "682 MB",
        },
    ]
