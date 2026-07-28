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