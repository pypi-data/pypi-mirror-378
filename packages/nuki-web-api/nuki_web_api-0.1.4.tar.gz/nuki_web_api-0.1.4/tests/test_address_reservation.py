from unittest.mock import patch, call


def test_list_reservations(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = [{"reservationId": "R1"}]
        result = client.address_reservation.list_reservations(123)

        mock_request.assert_has_calls([
            call("GET", "/address/123/reservation")
        ])
        assert isinstance(result, list)
        assert result[0]["reservationId"] == "R1"


def test_issue_reservation(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "issued"}
        result = client.address_reservation.issue_reservation(123, "R1")

        mock_request.assert_has_calls([
            call("POST", "/address/123/reservation/R1/issue")
        ])
        assert result["status"] == "issued"


def test_revoke_reservation(client):
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "revoked"}
        result = client.address_reservation.revoke_reservation(123, "R1")

        mock_request.assert_has_calls([
            call("POST", "/address/123/reservation/R1/revoke")
        ])
        assert result["status"] == "revoked"


def test_update_reservation_access_times(client):
    access_times = {"monday": ["08:00-10:00"]}
    with patch.object(client, "_request") as mock_request:
        mock_request.return_value = {"status": "updated"}
        result = client.address_reservation.update_reservation_access_times(123, "R1", access_times)

        mock_request.assert_has_calls([
            call("POST", "/address/123/reservation/R1/update/accesstimes", json=access_times)
        ])
        assert result["status"] == "updated"
