import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/users"
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

def test_api():
    """Runs a sequence of API tests."""
    user_id = None
    try:
        # 0. Test Validations
        print("STEP 0: Testing validations...")
        
        # Test invalid email
        invalid_email_payload = {
            "full_name": "Test User Python",
            "email": "test.python@gmail.com",
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
            "email": "test.python@perlametro.cl",
            "password": "weak"
        }
        print_request("POST", BASE_URL + "/", invalid_password_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(invalid_password_payload))
        print_response(response)
        assert response.status_code == 422, f"Expected status code 422 for invalid password, but got {response.status_code}"
        print("--- Invalid password validation passed ---\n")

        # 1. Create User
        print("STEP 1: Creating a new user...")
        create_payload = {
            "full_name": "Test User Python",
            "email": "test.python@perlametro.cl",
            "password": "Password123!"
        }
        print_request("POST", BASE_URL + "/", create_payload)
        response = requests.post(BASE_URL + "/", headers=HEADERS, data=json.dumps(create_payload))
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        user_id = response.json().get("id")
        print(f"--- User created successfully with ID: {user_id} ---\n")

        # 2. Get All Users
        print("STEP 2: Retrieving all users...")
        print_request("GET", BASE_URL + "/")
        response = requests.get(BASE_URL + "/", headers=HEADERS)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        print("--- Retrieved all users successfully ---\n")

        # 3. Get User by ID
        print(f"STEP 3: Retrieving user by ID ({user_id})...")
        print_request("GET", f"{BASE_URL}/{user_id}")
        response = requests.get(f"{BASE_URL}/{user_id}", headers=HEADERS)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.json().get("id") == user_id
        print("--- Retrieved user by ID successfully ---\n")

        # 4. Update User
        print(f"STEP 4: Updating user ({user_id})...")
        update_payload = {"full_name": "Updated Test User Python"}
        print_request("PUT", f"{BASE_URL}/{user_id}", update_payload)
        response = requests.put(f"{BASE_URL}/{user_id}", headers=HEADERS, data=json.dumps(update_payload))
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        assert response.json().get("full_name") == "Updated Test User Python"
        print("--- Updated user successfully ---\n")

        # 5. Soft Delete User
        print(f"STEP 5: Soft deleting user ({user_id})...")
        print_request("DELETE", f"{BASE_URL}/{user_id}")
        response = requests.delete(f"{BASE_URL}/{user_id}", headers=HEADERS)
        print_response(response)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        print("--- Soft deleted user successfully ---\n")

        # 6. Verify Soft Delete
        print(f"STEP 6: Verifying user ({user_id}) is no longer directly accessible...")
        print_request("GET", f"{BASE_URL}/{user_id}")
        response = requests.get(f"{BASE_URL}/{user_id}", headers=HEADERS)
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
