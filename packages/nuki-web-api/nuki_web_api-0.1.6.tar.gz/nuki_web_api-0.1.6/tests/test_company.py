from unittest.mock import patch, call


def test_list_companies(client):
    with patch.object(client, "_request") as mock_request:
        # Make the _request return a sample list of companies
        mock_request.return_value = [{"companyId": "C1", "name": "Acme Co"}]

        result = client.company.list_companies()

        mock_request.assert_has_calls([
            call("GET", "/company")
        ])
        assert isinstance(result, list)
        assert result[0]["companyId"] == "C1"
        assert result[0]["name"] == "Acme Co"
