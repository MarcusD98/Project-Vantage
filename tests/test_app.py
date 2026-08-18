from app import app

# The test_homepage_loads function essentially says "Pretend someone visited my homepage", and test whether the server responded successfully.

def test_homepage_loads():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200