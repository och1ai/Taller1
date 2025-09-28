import requests
import json
import sys
import random
import string

def generate_unique_email():
    """Generate a unique email with perlametro.cl domain"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test.{random_string}@perlametro.cl"

API_BASE = "http://localhost:8000/api/v1"
BASE_URL = f"{API_BASE}/users"
AUTH_URL = f"{API_BASE}/auth"
HEADERS = {"Content-Type": "application/json"}

def print_request(method, url, payload=None):
    """Prints the outgoing request details."""
    print("="*80)
    print(f"--> REQUEST: {method} {url}")
    if payload:
        print(f"--> PAYLOAD:\n{json.dumps(payload, indent=4)}")
    print("="*80)

def print_response(response):
    """Prints the incoming response details."""
    print(f"<-- STATUS CODE: {response.status_code}")
    try:
        print(f"<-- RESPONSE:\n{json.dumps(response.json(), indent=4)}")
    except json.JSONDecodeError:
        print(f"<-- RESPONSE (non-JSON):\n{response.text}")
    print("="*80)
    print("\n")

def test_auth():
    """Test authentication endpoints and functionality."""
    print("\nTESTING AUTHENTICATION...")
    print("="*80)

    # 1. Test login with invalid credentials
    print("\nStep 1: Testing login with invalid credentials...")
    login_payload = {
        "email": "nonexistent@perlametro.cl",
        "password": "wrong_password"
    }
    print_request("POST", f"{AUTH_URL}/login", login_payload)
    response = requests.post(f"{AUTH_URL}/login", headers=HEADERS, json=login_payload)
    print_response(response)
    assert response.status_code == 401, "Expected 401 for invalid credentials"
    print("--- Invalid credentials test passed ---\n")

    # 2. Register and login with a regular user
    print("Step 2: Creating a regular user for login test...")
    regular_email = generate_unique_email()
    regular_password = "Password123!"
    user_payload = {
        "full_name": "Regular Test User",
        "email": regular_email,
        "password": regular_password
    }
    print_request("POST", f"{BASE_URL}/", user_payload)
    response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=user_payload)
    print_response(response)
    assert response.status_code == 200, "Failed to create test user"
    regular_user_id = response.json()["id"]

    # 3. Login with the regular user
    print("Step 3: Testing login with regular user...")
    login_payload = {
        "email": regular_email,
        "password": regular_password
    }
    print_request("POST", f"{AUTH_URL}/login", login_payload)
    response = requests.post(f"{AUTH_URL}/login", headers=HEADERS, json=login_payload)
    print_response(response)
    assert response.status_code == 200, "Login failed"
    regular_token = response.json()["access_token"]
    assert response.json()["is_admin"] is False, "Regular user should not be admin"
    print("--- Regular user login test passed ---\n")

    # 4. Try to access users list with regular user token (should work now)
    print("Step 4: Testing user list access with regular user token...")
    user_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {regular_token}"
    }
    print_request("GET", f"{BASE_URL}/", None)
    response = requests.get(f"{BASE_URL}/", headers=user_headers)
    print_response(response)
    assert response.status_code == 200, "Regular user should be able to access user list"
    print("--- Regular user access test passed ---\n")

    # 4.1 Test user updating their own profile
    print("Step 4.1: Testing user updating their own profile...")
    update_payload = {
        "full_name": "Updated Regular User"
    }
    print_request("PUT", f"{BASE_URL}/{regular_user_id}", update_payload)
    response = requests.put(f"{BASE_URL}/{regular_user_id}", headers=user_headers, json=update_payload)
    print_response(response)
    assert response.status_code == 200, "User should be able to update their own profile"
    assert response.json()["full_name"] == "Updated Regular User", "Name should be updated"
    print("--- Self profile update test passed ---\n")

    # 4.2 Try to update another user's profile (should fail)
    print("Step 4.2: Testing user updating another user's profile...")
    # Obtener la lista de usuarios para encontrar a john.doe
    print_request("GET", f"{BASE_URL}/", None)
    users_response = requests.get(f"{BASE_URL}/", headers=user_headers)
    print_response(users_response)
    # Intentar actualizar al usuario john.doe
    john_doe_users = [user for user in users_response.json() if user["email"] == "john.doe@perlametro.cl"]
    other_user_id = john_doe_users[0]["id"]
    update_payload = {
        "full_name": "Trying to update other user"
    }
    print_request("PUT", f"{BASE_URL}/{other_user_id}", update_payload)
    response = requests.put(f"{BASE_URL}/{other_user_id}", headers=user_headers, json=update_payload)
    print_response(response)
    assert response.status_code == 403, "User should not be able to update other users' profiles"
    print("--- Other profile update restriction test passed ---\n")

    # 4.3 Try to delete a user with regular user token (should fail)
    print("Step 4.3: Testing delete user with regular user token...")
    print_request("DELETE", f"{BASE_URL}/{regular_user_id}", None)
    response = requests.delete(f"{BASE_URL}/{regular_user_id}", headers=user_headers)
    print_response(response)
    assert response.status_code == 403, "Regular user should not be able to delete users"
    print("--- Delete restriction test passed ---\n")

    # 5. Login with admin user
    print("Step 5: Testing login with admin user...")
    admin_login_payload = {
        "email": "admin@perlametro.cl",
        "password": "Password123!"
    }
    print_request("POST", f"{AUTH_URL}/login", admin_login_payload)
    response = requests.post(f"{AUTH_URL}/login", headers=HEADERS, json=admin_login_payload)
    print_response(response)
    assert response.status_code == 200, "Admin login failed"
    admin_token = response.json()["access_token"]
    assert response.json()["is_admin"] is True, "Admin user should have admin flag"
    print("--- Admin login test passed ---\n")

    # 6. Test admin operations
    print("Step 6: Testing admin operations...")
    admin_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    }
    
    # 6.1 Test user list access
    print("Step 6.1: Testing user list access with admin token...")
    print_request("GET", f"{BASE_URL}/", None)
    response = requests.get(f"{BASE_URL}/", headers=admin_headers)
    print_response(response)
    assert response.status_code == 200, "Admin should have access to user list"
    print("--- Admin list access test passed ---\n")
    
    # 6.2 Test user deletion
    print("Step 6.2: Testing user deletion with admin token...")
    print_request("DELETE", f"{BASE_URL}/{regular_user_id}", None)
    response = requests.delete(f"{BASE_URL}/{regular_user_id}", headers=admin_headers)
    print_response(response)
    assert response.status_code == 200, "Admin should be able to delete users"
    print("--- Admin delete operation test passed ---\n")

    # 7. Check session info
    print("Step 7: Testing session info endpoint...")
    print_request("GET", f"{AUTH_URL}/session", None)
    response = requests.get(f"{AUTH_URL}/session", headers=admin_headers)
    print_response(response)
    assert response.status_code == 200, "Failed to get session info"
    session_info = response.json()
    assert session_info["is_admin"] is True, "Session should reflect admin status"
    assert "expires_at" in session_info, "Session should include expiration time"
    print("--- Session info test passed ---\n")

    return admin_headers

def test_api():
    """Runs a sequence of API tests."""
    global HEADERS  # Para poder modificar los headers globales
    user_id = None
    admin_token = None
    try:
        # 0. Test Validations (without authentication)
        print("STEP 0: Testing validations...")
        
        # Test invalid email
        invalid_email_payload = {
            "full_name": "Test User Python",
            "email": "test.user@gmail.com",  # Non-institutional email
            "password": "Password123!"
        }
        print_request("POST", BASE_URL + "/", invalid_email_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(invalid_email_payload))
        print_response(response)
        assert response.status_code == 422, f"Expected status code 422 for invalid email, but got {response.status_code}"
        print("--- Invalid email validation passed ---\n")

        # Test invalid password
        invalid_password_payload = {
            "full_name": "Test User Python",
            "email": generate_unique_email(),
            "password": "weak"
        }
        print_request("POST", BASE_URL + "/", invalid_password_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(invalid_password_payload))
        print_response(response)
        assert response.status_code == 422, f"Expected status code 422 for invalid password, but got {response.status_code}"
        print("--- Invalid password validation passed ---\n")

        # Test viewing users without authentication (should fail)
        print("Testing user list access without authentication...")
        print_request("GET", BASE_URL + "/")
        response = requests.get(BASE_URL + "/", headers=HEADERS)
        print_response(response)
        assert response.status_code == 401, f"Expected status code 401 for unauthorized access, but got {response.status_code}"
        print("--- Unauthorized access test passed ---\n")
        
        # First run authentication tests and get admin token
        admin_headers = test_auth()
        # Extract the admin token from the headers
        admin_token = admin_headers.get("Authorization", "").replace("Bearer ", "")
        
        # Test successful user registration
        print("STEP 0.1: Testing successful user registration without authentication...")
        registration_payload = {
            "full_name": "Test User Python",
            "email": generate_unique_email(),
            "password": "Password123!"
        }
        print_request("POST", BASE_URL + "/", registration_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(registration_payload))
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200 for successful registration, but got {response.status_code}"
        assert "is_admin" in response.json() and not response.json()["is_admin"], "New user should not be admin"
        print("--- User registration test passed ---\n")

        # 1. Create User
        print("STEP 1: Creating a new user...")
        
        create_payload = {
            "full_name": "Test User Python",
            "email": generate_unique_email(),
            "password": "Password123!",
            "is_admin": True  # Attempt to create an admin user through API
        }
        print_request("POST", BASE_URL + "/", create_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(create_payload))
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        user_response = response.json()
        user_id = user_response.get("id")
        assert "is_admin" in user_response, "Response should include is_admin field"
        assert user_response["is_admin"] is False, "API should ignore is_admin flag in request"
        print(f"--- User created successfully with ID: {user_id} (verified non-admin) ---\n")
        
        # 2. Get All Users (now requires authentication)
        print("STEP 2: Retrieving all users...")
        admin_headers = {"Content-Type": "application/json", "Authorization": "Bearer " + admin_token}
        print_request("GET", BASE_URL + "/")
        response = requests.get(BASE_URL + "/", headers=admin_headers)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        print("--- Retrieved all users successfully ---\n")

        # 2.1 Verify user list contains the is_admin field and that we can't create admin users via API
        users = response.json()
        assert all("is_admin" in user for user in users), "All users should have the is_admin field"
        assert all(not user["is_admin"] for user in users if user["email"] != "admin@perlametro.cl"), "Regular users should not be admins"
        print("--- Admin flag presence and restriction verification passed ---\n")

        # 3. Get User by ID
        print(f"STEP 3: Retrieving user by ID ({user_id})...")
        print_request("GET", f"{BASE_URL}/{user_id}")
        response = requests.get(f"{BASE_URL}/{user_id}", headers=admin_headers)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        user_response = response.json()
        assert user_response.get("id") == user_id
        assert "is_admin" in user_response, "Response should include is_admin field"
        assert user_response["is_admin"] is False, "New users should not be admins"
        print("--- Retrieved user by ID successfully (with admin flag) ---\n")

        # 4. Update User
        print(f"STEP 4: Updating user ({user_id})...")
        update_payload = {"full_name": "Updated Test User Python"}
        print_request("PUT", f"{BASE_URL}/{user_id}", update_payload)
        response = requests.put(f"{BASE_URL}/{user_id}", headers=admin_headers, data=json.dumps(update_payload))
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.json().get("full_name") == "Updated Test User Python"
        print("--- Updated user successfully ---\n")

        # 5. Soft Delete User
        print(f"STEP 5: Soft deleting user ({user_id})...")
        print_request("DELETE", f"{BASE_URL}/{user_id}")
        response = requests.delete(f"{BASE_URL}/{user_id}", headers=admin_headers)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        print("--- Soft deleted user successfully ---\n")

        # 6. Verify Soft Delete
        print(f"STEP 6: Verifying user ({user_id}) is no longer directly accessible...")
        print_request("GET", f"{BASE_URL}/{user_id}")
        response = requests.get(f"{BASE_URL}/{user_id}", headers=admin_headers)
        print_response(response)
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
        print("--- Verified user is not found (soft delete successful) ---\n")

        print("✅ All tests passed successfully!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API CONNECTION FAILED: {e}")
        print("Please ensure the Docker services are running with 'bash start-local.sh'")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
