from httpx import AsyncClient



async def test_register_user(client: AsyncClient):
	response = await client.post(
		"/api/v1/auth/register",
		json={
			"email": "test@example.com",
			"password": "strong-password",
		},
	)	

	assert response.status_code == 201

	data = response.json()
	assert isinstance(data["id"], int)
	assert data["id"] > 0
	assert data["email"] == "test@example.com"
	assert data["is_active"] is True


async def test_register_duplicate_email(client: AsyncClient):
	user_data = {
		"email": "test@example.com",
		"password": "strong-password",
	}

	first_response = await client.post("/api/v1/auth/register", json=user_data)

	assert first_response.status_code == 201

	second_response = await client.post("/api/v1/auth/register", json=user_data)

	assert second_response.status_code == 400


async def test_login_returns_access_token(client: AsyncClient):
	user_data = {
		"email": "test@example.com",
		"password": "strong-password",
	}

	register_response = await client.post("/api/v1/auth/register", json=user_data)

	assert register_response.status_code == 201

	login_response = await client.post("/api/v1/auth/login", json=user_data)

	assert login_response.status_code == 200

	data = login_response.json()
	assert isinstance(data["access_token"], str)
	assert data["token_type"] == "bearer"


async def test_login_with_wrong_password(client: AsyncClient):
	await client.post("/api/v1/auth/register", json={
		"email": "test@example.com",
		"password": "strong-password",
	})

	response = await client.post("/api/v1/auth/login", json={
		"email": "test@example.com",
		"password": "wrong-password",
	})

	assert response.status_code == 401


async def test_register_with_invalid_email(client: AsyncClient):
	response = await client.post(
		"/api/v1/auth/register",
		json={
			"email": "not-an-email",
			"password": "strong-password"
		}
	)

	assert response.status_code == 422


async def test_get_me_returns_current_user(
	client: AsyncClient,
	fake_redis,	
):
	user_data = {
		"email": "test@example.com",
		"password": "strong-password",
	}

	await client.post("/api/v1/auth/register", json=user_data)

	login_response = await client.post("/api/v1/auth/login", json=user_data)
	token = login_response.json()["access_token"]

	response = await client.get(
		"/api/v1/auth/me",
		headers={"Authorization": f"Bearer {token}"},
	)

	assert response.status_code == 200
	assert response.json()["email"] == user_data["email"]


async def test_logout_blacklists_token(
	client: AsyncClient,
	fake_redis,
):
	user_data = {
		"email": "test@example.com",
		"password": "strong-password",
	}

	await client.post("/api/v1/auth/register", json=user_data)

	login_response = await client.post("/api/v1/auth/login", json=user_data)
	token = login_response.json()["access_token"]
	headers={"Authorization": f"Bearer {token}"}

	logout_response = await client.post(
		"/api/v1/auth/logout",
		headers=headers,
	)

	assert logout_response.status_code == 200

	me_response = await client.get(
		"/api/v1/auth/me",
		headers=headers
	)
