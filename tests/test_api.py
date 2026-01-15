from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


class TestCreateVoucher:
    def test_create_voucher_success(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["discount_percent"] == 20
        assert data["is_active"] is True
        assert len(data["code"]) == 8
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_voucher_invalid_discount_too_low(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        response = client.post(
            "/vouchers/",
            json={"discount_percent": 0, "expires_at": expires_at},
        )
        assert response.status_code == 422

    def test_create_voucher_invalid_discount_too_high(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        response = client.post(
            "/vouchers/",
            json={"discount_percent": 101, "expires_at": expires_at},
        )
        assert response.status_code == 422

    def test_create_voucher_missing_fields(self, client: TestClient) -> None:
        response = client.post("/vouchers/", json={})
        assert response.status_code == 422

    def test_create_voucher_invalid_expires_at(self, client: TestClient) -> None:
        response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": "not-a-date"},
        )
        assert response.status_code == 422


class TestListVouchers:
    def test_list_vouchers_empty(self, client: TestClient) -> None:
        response = client.get("/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 20

    def test_list_vouchers_with_data(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        for i in range(3):
            client.post(
                "/vouchers/",
                json={"discount_percent": 10 + i, "expires_at": expires_at},
            )

        response = client.get("/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_list_vouchers_pagination(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        for i in range(5):
            client.post(
                "/vouchers/",
                json={"discount_percent": 10 + i, "expires_at": expires_at},
            )

        response = client.get("/vouchers/?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["skip"] == 2
        assert data["limit"] == 2

    def test_list_vouchers_limit_max(self, client: TestClient) -> None:
        response = client.get("/vouchers/?limit=101")
        assert response.status_code == 422

    def test_list_vouchers_skip_negative(self, client: TestClient) -> None:
        response = client.get("/vouchers/?skip=-1")
        assert response.status_code == 422

    def test_list_vouchers_excludes_inactive(self, client: TestClient) -> None:
        """Inactive vouchers should not appear in list."""
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()

        # Create 3 vouchers
        codes = []
        for i in range(3):
            resp = client.post(
                "/vouchers/",
                json={"discount_percent": 10 + i, "expires_at": expires_at},
            )
            codes.append(resp.json()["code"])

        # Deactivate one
        client.delete(f"/vouchers/{codes[0]}")

        response = client.get("/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        returned_codes = [v["code"] for v in data["items"]]
        assert codes[0] not in returned_codes

    def test_list_vouchers_excludes_expired(self, client: TestClient, db_session) -> None:
        """Expired vouchers should not appear in list."""
        from app.models import Voucher

        # Create an expired voucher directly in db
        expired_voucher = Voucher(
            discount_percent=10,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        db_session.add(expired_voucher)
        db_session.commit()

        # Create an active voucher via API
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )

        response = client.get("/vouchers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["discount_percent"] == 20


class TestGetVoucher:
    def test_get_voucher_success(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 25, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.get(f"/vouchers/{code}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == code
        assert data["discount_percent"] == 25

    def test_get_voucher_not_found(self, client: TestClient) -> None:
        response = client.get("/vouchers/NOTEXIST")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_voucher_inactive_returns_404(self, client: TestClient) -> None:
        """Inactive vouchers should return 404."""
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 25, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        # Deactivate the voucher
        client.delete(f"/vouchers/{code}")

        # Try to get it
        response = client.get(f"/vouchers/{code}")
        assert response.status_code == 404

    def test_get_voucher_expired_returns_404(self, client: TestClient, db_session) -> None:
        """Expired vouchers should return 404."""
        from app.models import Voucher

        # Create an expired voucher directly in db
        expired_voucher = Voucher(
            discount_percent=10,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        db_session.add(expired_voucher)
        db_session.commit()
        db_session.refresh(expired_voucher)

        response = client.get(f"/vouchers/{expired_voucher.code}")
        assert response.status_code == 404


class TestUpdateVoucher:
    def test_update_voucher_discount(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.patch(
            f"/vouchers/{code}",
            json={"discount_percent": 30},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == 30

    def test_update_voucher_expires_at(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        new_expires_at = (datetime.now(UTC) + timedelta(days=60)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.patch(
            f"/vouchers/{code}",
            json={"expires_at": new_expires_at},
        )

        assert response.status_code == 200

    def test_update_voucher_is_active(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.patch(
            f"/vouchers/{code}",
            json={"is_active": False},
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_update_voucher_not_found(self, client: TestClient) -> None:
        response = client.patch(
            "/vouchers/NOTEXIST",
            json={"discount_percent": 30},
        )
        assert response.status_code == 404

    def test_update_voucher_invalid_discount(self, client: TestClient) -> None:
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.patch(
            f"/vouchers/{code}",
            json={"discount_percent": 150},
        )
        assert response.status_code == 422

    def test_update_voucher_partial(self, client: TestClient) -> None:
        """Test that PATCH only updates provided fields."""
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        original = create_response.json()
        code = original["code"]

        response = client.patch(
            f"/vouchers/{code}",
            json={"discount_percent": 50},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == 50
        assert data["is_active"] == original["is_active"]


class TestDeactivateVoucher:
    def test_deactivate_voucher_success(self, client: TestClient, db_session) -> None:
        """Delete should soft-delete (set is_active=False), not remove record."""
        from app.models import Voucher

        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        response = client.delete(f"/vouchers/{code}")

        assert response.status_code == 204

        # Verify record still exists in db but is inactive
        voucher = db_session.query(Voucher).filter(Voucher.code == code).first()
        assert voucher is not None
        assert voucher.is_active is False

    def test_deactivate_voucher_not_found(self, client: TestClient) -> None:
        response = client.delete("/vouchers/NOTEXIST")
        assert response.status_code == 404

    def test_deactivate_voucher_idempotent(self, client: TestClient) -> None:
        """Deactivating an already inactive voucher should succeed."""
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        client.delete(f"/vouchers/{code}")
        response = client.delete(f"/vouchers/{code}")

        assert response.status_code == 204

    def test_deactivate_removes_from_list(self, client: TestClient) -> None:
        """Deactivated voucher should not appear in list."""
        expires_at = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        create_response = client.post(
            "/vouchers/",
            json={"discount_percent": 20, "expires_at": expires_at},
        )
        code = create_response.json()["code"]

        # Verify it's in the list
        list_response = client.get("/vouchers/")
        assert len(list_response.json()["items"]) == 1

        # Deactivate
        client.delete(f"/vouchers/{code}")

        # Verify it's no longer in the list
        list_response = client.get("/vouchers/")
        assert len(list_response.json()["items"]) == 0


class TestHealthCheck:
    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
