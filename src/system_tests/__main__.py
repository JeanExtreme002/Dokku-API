import secrets
import sys
import time

import requests

if len(sys.argv) != 4:
    print(sys.argv)
    raise ValueError("Usage: python test_app.py <base_url> <master_key> <api_key>")

BASE_URL = sys.argv[1]
MASTER_KEY = sys.argv[2]
API_KEY = sys.argv[3]

print(f"Testing API at {BASE_URL} with MASTER_KEY={MASTER_KEY} and API_KEY={API_KEY}")

test_id = str(time.time()).replace(".", "")

user_email = f"test{test_id}@example.com"
user_token = secrets.token_urlsafe(256)
user_app = "test-app"
user_app_domain = "testdokkuapi.com"
user_app_repo_url = "https://github.com/heroku/ruby-getting-started"
user_app_key = f"key{secrets.token_hex(8)}"
user_app_key_value = secrets.token_hex(8)
user_app_port_mapping = {"protocol": "http", "origin": 5300, "dest": 7040}
user_database = "test_database"
user_network = "test_network"

# Check base endpoints
print("Test: Checking base endpoints...")
response = requests.get(BASE_URL)
assert response.status_code == 200

response = requests.get(BASE_URL + "/api")
response_json = response.json()
assert response.status_code == 200
assert response_json["dokku_status"] == True

response = requests.get(BASE_URL + "/api/list-databases")
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == [
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "mariadb",
    "couchdb",
    "cassandra",
    "elasticsearch",
    "influxdb",
]

# Create a new user
print("Test: Creating a new user...")
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email}?access_token={user_token}",
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"},
)
assert response.status_code == 201

# Must not create with a existing email.
print("Test: Must not create with an existing email...")
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email}",
    params={"access_token": user_token + "new"},
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"},
)
assert response.status_code != 201

# Must not create with a existing token.
print("Test: Must not create with an existing token...")
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email + 'new'}",
    params={"access_token": user_token},
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"},
)
assert response.status_code != 201

# Create a new user again (double-check)
print("Test: Creating a new user again (double-check)...")
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email + 'new'}",
    params={"access_token": user_token + "new"},
    headers={"MASTER-KEY": MASTER_KEY},
)
assert response.status_code == 201

# Check user credentials
print("Test: Checking user credentials...")
response = requests.post(
    BASE_URL + "/api/apps/list",
    params={"api_key": "invalid"},
    json={"access_token": user_token},
)
assert response.status_code == 401

response = requests.post(
    BASE_URL + "/api/apps/list",
    params={"api_key": API_KEY},
    json={"access_token": "invalid"},
)
assert response.status_code == 401

response = requests.post(
    BASE_URL + "/api/quota",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json == {"apps_quota": 0, "services_quota": 0, "networks_quota": 0}

# Check admin credentials
print("Test: Checking admin credentials...")
response = requests.post(
    BASE_URL + "/api/admin/users/list", headers={"MASTER-KEY": "invalid_key"}
)
response_json = response.json()
assert response.status_code == 401

# Increase user quota
print("Test: Increasing user quota...")
response = requests.put(
    BASE_URL + f"/api/admin/users/{user_email}/quota",
    params={
        "apps_quota": 1,
        "services_quota": 1,
        "networks_quota": 1,
    },
    headers={"MASTER-KEY": MASTER_KEY},
)
response_json = response.json()
assert response.status_code == 200

response = requests.post(
    BASE_URL + "/api/quota",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json == {"apps_quota": 1, "services_quota": 1, "networks_quota": 1}

# Create new app
print("Test: Creating a new app...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 201
assert response_json["success"] == True

# Must not exceed quota
print("Test: Must not exceed quota when creating a new app...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app + 'new'}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Get app information
print("Test: Getting app information...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/info",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"]["data"]["deployed"] == "false"

# Get app URL
print("Test: Getting app URL...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/url",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Get app logs
print("Test: Getting app logs...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/logs",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200

# Get app deployment token
print("Test: Getting app deployment token...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/deployment-token",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert len(response_json["result"]) > 0

# Set app configuration
print("Test: Setting app configuration...")
response = requests.post(
    BASE_URL + f"/api/config/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {}

response = requests.post(
    BASE_URL + f"/api/config/{user_app}/{user_app_key}/{user_app_key_value}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

response = requests.post(
    BASE_URL + f"/api/config/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {user_app_key: user_app_key_value}

# Create new database
print("Test: Creating a new database...")
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 201
assert response_json["success"] == True


# Must not exceed quota
print("Test: Must not exceed quota when creating a new database...")
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database + 'new'}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Get database information
print("Test: Getting database information...")
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/info",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"]["plugin_name"] == "mysql"

# Link app to database
print("Test: Linking app to database...")
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/linked-apps",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == []

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/databases",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {}

response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/link/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/linked-apps",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == [
    user_app,
]

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/databases",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {"mysql": [user_database]}

# Create new network
print("Test: Creating a new network...")
response = requests.post(
    BASE_URL + f"/api/networks/{user_network}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 201
assert response_json["success"] == True

# Must not exceed quota
print("Test: Must not exceed quota when creating a new network...")
response = requests.post(
    BASE_URL + f"/api/networks/{user_network + 'new'}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Link app to network
print("Test: Linking app to network...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/network",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {"network": None}

response = requests.post(
    BASE_URL + f"/api/networks/{user_network}/link/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/network",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {"network": user_network}

response = requests.post(
    BASE_URL + f"/api/networks/{user_network}/linked-apps",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == [
    user_app,
]

# Deploy application
print("Test: Deploying application...")
response = requests.put(
    BASE_URL + f"/api/deploy/{user_app}",
    params={"api_key": API_KEY, "repo_url": user_app_repo_url},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Setting domain for the app
print("Test: Setting domain for the app...")
response = requests.post(
    BASE_URL + f"/api/domains/{user_app}/{user_app_domain}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Unsetting domain for the app
print("Test: Unsetting domain for the app...")
response = requests.delete(
    BASE_URL + f"/api/domains/{user_app}/{user_app_domain}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Setting port mapping
print("Test: Setting port mapping for the app...")
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/ports",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == []

response = requests.post(
    BASE_URL
    + f"/api/apps/{user_app}/ports/{user_app_port_mapping['protocol']}/{user_app_port_mapping['origin']}/{user_app_port_mapping['dest']}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/ports",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == [
    user_app_port_mapping,
]

# Unsetting port mapping
print("Test: Unsetting port mapping for the app...")
response = requests.delete(
    BASE_URL
    + f"/api/apps/{user_app}/ports/{user_app_port_mapping['protocol']}/{user_app_port_mapping['origin']}/{user_app_port_mapping['dest']}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/ports",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == []

# Unlink app from network
print("Test: Unlinking app from network...")
response = requests.delete(
    BASE_URL + f"/api/networks/{user_network}/link/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/network",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {"network": None}

# Unlink app from database
print("Test: Unlinking app from database...")
response = requests.delete(
    BASE_URL + f"/api/databases/mysql/{user_database}/link/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/databases",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True
assert response_json["result"] == {}

# Delete network
print("Test: Deleting network...")
response = requests.delete(
    BASE_URL + f"/api/networks/{user_network}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Delete database
print("Test: Deleting database...")
response = requests.delete(
    BASE_URL + f"/api/databases/mysql/{user_database}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True

# Delete app
print("Test: Deleting app...")
response = requests.delete(
    BASE_URL + f"/api/apps/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token},
)
response_json = response.json()
assert response.status_code == 200
assert response_json["success"] == True


print("All tests passed successfully!")
