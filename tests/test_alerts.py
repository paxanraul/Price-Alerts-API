from httpx import AsyncClient


ALERT_DATA = {
	"symbol": "BTC",
	"condition": ">",
	"threshold": 100.0,
	"channel": "webhook",
	"channel_target": "http://example.com",
	"cooldown_seconds": 300,
}


async def get_auth_headers(
	client: AsyncClient,
	email: str,
) -> dict[str, str]:
	user_data = {
		"email": email,
		"password": "strong-password",
	}

	register_response = await client.post(
		"/api/v1/auth/register",
		json=user_data,
	)
	assert register_response.status_code == 201

	login_response = await client.post(
		"/api/v1/auth/login",
		json=user_data,
	)
	assert login_response.status_code == 200

	token = login_response.json()["access_token"]

	return {"Authorization": f"Bearer {token}"}


async def test_create_alert(
	client: AsyncClient,
	fake_redis,
	disable_rate_limit,
):
	headers = await get_auth_headers(client, "owner@example.com")

	response = await client.post(
		"/api/v1/alerts",
		headers=headers,
		json=ALERT_DATA,
	)

	assert response.status_code == 201

	data = response.json()
	assert isinstance(data["id"], int)
	assert data["symbol"] == ALERT_DATA["symbol"]
	assert data["condition"] == ALERT_DATA["condition"]
	assert data["threshold"] == ALERT_DATA["threshold"]
	assert data["state"] == "armed"
	assert data["is_active"] is True


async def test_list_alerts_returns_only_current_users(
	client: AsyncClient,
	fake_redis,
	disable_rate_limit,
):
	owner_headers = await get_auth_headers(
		client,
		"owner@example.com",
	)

	other_headers = await get_auth_headers(
		client,
		"other@example.com",
	)

	owner_create_response = await client.post(
		"/api/v1/alerts",
		headers=owner_headers,
		json=ALERT_DATA,
	)
	assert owner_create_response.status_code == 201

	other_create_response = await client.post(
		"/api/v1/alerts",
		headers=other_headers,
		json=ALERT_DATA,
	)
	assert other_create_response.status_code == 201

	response = await client.get(
		"/api/v1/alerts",
		headers=owner_headers,
	)

	assert response.status_code == 200

	alerts = response.json()
	assert len(alerts) == 1
	assert alerts[0]["id"] == owner_create_response.json()["id"]


async def test_get_alert_by_id(
		client: AsyncClient,
		fake_redis,
		disable_rate_limit,
):
	headers = await get_auth_headers(client, "owner@example.com")

	create_response = await client.post(
		"/api/v1/alerts",
		headers=headers,
		json=ALERT_DATA,
	)
	assert create_response.status_code == 201

	alert_id = create_response.json()["id"]

	response = await client.get(
		f"/api/v1/alerts/{alert_id}",
		headers=headers,
	)

	assert response.status_code == 200

	data = response.json()
	assert data["id"] == alert_id
	assert data["symbol"] == ALERT_DATA["symbol"]
	assert data["threshold"] == ALERT_DATA["threshold"]


async def test_update_alert_threshold(
		client: AsyncClient,
		fake_redis,
		disable_rate_limit,
):
	headers = await get_auth_headers(client, "owner@example.com")

	create_response = await client.post(
		"/api/v1/alerts",
		headers=headers,
		json=ALERT_DATA,
	)
	assert create_response.status_code == 201

	alert_id = create_response.json()["id"]

	response = await client.patch(
		f"/api/v1/alerts/{alert_id}",
		headers=headers,
		json={"threshold": 200.0},
	)

	assert response.status_code == 200
	assert response.json()["threshold"] == 200

	get_response = await client.get(
		f"/api/v1/alerts/{alert_id}",
		headers=headers,
	)

	assert get_response.status_code == 200
	assert get_response.json()["threshold"] == 200.0


async def test_delete_alert_deactivates_it(
		client: AsyncClient,
		fake_redis,
		disable_rate_limit,
):
	headers = await get_auth_headers(client, "owner@example.com")

	create_response = await client.post(
		"/api/v1/alerts",
		headers=headers,
		json=ALERT_DATA,
	)
	assert create_response.status_code == 201

	alert_id = create_response.json()["id"]

	delete_response = await client.delete(
		f"/api/v1/alerts/{alert_id}",
		headers=headers,
	)

	assert delete_response.status_code == 204

	get_response = await client.get(
		f"/api/v1/alerts/{alert_id}",
		headers=headers,
	)

	assert get_response.status_code == 200
	assert get_response.json()["is_active"] is False


async def test_other_user_cannot_access_or_update_alert(
		client: AsyncClient,
		fake_redis,
		disable_rate_limit,
):
	owner_headers = await get_auth_headers(client, "owner@example.com")
	other_headers = await get_auth_headers(client, "other@example.com")

	create_response = await client.post(
		"/api/v1/alerts",
		headers=owner_headers,
		json=ALERT_DATA,
	)
	assert create_response.status_code == 201

	alert_id = create_response.json()["id"]

	update_response = await client.patch(
		f"/api/v1/alerts/{alert_id}",
		headers=other_headers,
		json={"threshold": 200.0},
	)
	assert update_response.status_code == 404
