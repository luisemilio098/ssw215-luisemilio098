import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from github_service import fetch_readme


def test_fetch_readme_limits_response_to_4000_characters():
    fake_readme = "x" * 5000
    response = MagicMock()
    response.status_code = 200
    response.text = fake_readme

    with patch("github_service.requests.get", return_value=response) as mock_get:
        result = fetch_readme("octocat", "hello-world")

    assert len(result) == 4000
    mock_get.assert_called_once()
