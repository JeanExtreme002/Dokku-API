import requests
import secrets
import sys

if len(sys.argv) != 4:
    print(sys.argv)
    raise ValueError("Usage: python test_app.py <base_url> <master_key> <api_key>")

BASE_URL = sys.argv[1]
MASTER_KEY = sys.argv[2]
API_KEY = sys.argv[3]

print(f"Testing API at {BASE_URL} with MASTER_KEY={MASTER_KEY} and API_KEY={API_KEY}")

user_email = f"test{secrets.token_hex(16)}@example.com"
user_token = secrets.token_urlsafe(256)
user_app = "test-app"
user_app_repo_url = "https://github.com/heroku/ruby-getting-started"
user_app_key = f"key{secrets.token_hex(8)}"
user_app_key_value = secrets.token_hex(8)
user_database = "test_database"
user_network = "test_network"

# Check base endpoints
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
    "influxdb"
]

# Create a new user
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email}?access_token={user_token}",
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"}
)
assert response.status_code == 201

# Must not create with a existing email.
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email}",
    params={"access_token": user_token + "new"},
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"}
)
assert response.status_code != 201

# Must not create with a existing token.
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email + 'new'}",
    params={"access_token": user_token},
    headers={"MASTER-KEY": MASTER_KEY, "Content-Type": "application/json"}
)
assert response.status_code != 201

# Create a new user again (double-check)
response = requests.post(
    BASE_URL + f"/api/admin/users/{user_email + 'new'}",
    params={"access_token": user_token + "new"},
    headers={"MASTER-KEY": MASTER_KEY}
)
assert response.status_code == 201

# Check user credentials
response = requests.post(
    BASE_URL + "/api/apps/list", 
    params={"api_key": "invalid"}, 
    json={"access_token": user_token}
)
assert response.status_code == 401

response = requests.post(
    BASE_URL + "/api/apps/list", 
    params={"api_key": API_KEY}, 
    json={"access_token": "invalid"}
)
assert response.status_code == 401

response = requests.post(
    BASE_URL + "/api/quota", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json == {
    "apps_quota": 0,
    "services_quota": 0,
    "networks_quota": 0,
    "storage_quota": 0
}

# Check admin credentials
response = requests.post(
    BASE_URL + "/api/admin/users/list", 
    headers={"MASTER-KEY": "invalid_key"}
)
response_json = response.json()
assert response.status_code == 401

# Increase user quota
response = requests.put(
    BASE_URL + f"/api/admin/users/{user_email}/quota",
    params={
        "apps_quota": 1,
        "services_quota": 1,
        "networks_quota": 1,
    },
    headers={"MASTER-KEY": MASTER_KEY}
)
assert response.status_code == 200

response = requests.post(
    BASE_URL + "/api/quota", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json == {
    "apps_quota": 1,
    "services_quota": 1,
    "networks_quota": 1,
    "storage_quota": 0
}

# Create new app
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
assert response.status_code == 201

# Must not exceed quota
response = requests.post(
    BASE_URL + f"/api/apps/{user_app + 'new'}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Get app information
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/info", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"]["data"]["deployed"] == "false"

# Get app URL
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/url",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
assert response.status_code == 200

# Get app logs
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/logs",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
assert response.status_code == 200

# Get app deployment token
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/deployment-token",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert len(response_json["result"]) > 0

# Set app configuration
response = requests.post(
    BASE_URL + f"/api/config/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {}

response = requests.post(
    BASE_URL + f"/api/config/{user_app}/{user_app_key}/{user_app_key_value}",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200

response = requests.post(
    BASE_URL + f"/api/config/{user_app}",
    params={"api_key": API_KEY},
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {user_app_key: user_app_key_value}

# Create new database
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
assert response.status_code == 201

# Must not exceed quota
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database + 'new'}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Get database information
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/info", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"]["plugin_name"] == "mysql"

# Link app to database
response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/linked-apps", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == []

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/databases", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {}

response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/link/{user_app}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
assert response.status_code == 200

response = requests.post(
    BASE_URL + f"/api/databases/mysql/{user_database}/linked-apps", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == [user_app,]

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/databases", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {'mysql': [user_database]}

# Create new network
response = requests.post(
    BASE_URL + f"/api/networks/{user_network}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
assert response.status_code == 201

# Must not exceed quota
response = requests.post(
    BASE_URL + f"/api/networks/{user_network + 'new'}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 403
assert response_json == {"detail": "Quota exceeded"}

# Link app to network
response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/network", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {'network': None}

response = requests.post(
    BASE_URL + f"/api/networks/{user_network}/link/{user_app}", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200

response = requests.post(
    BASE_URL + f"/api/apps/{user_app}/network", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == {'network': user_network}

response = requests.post(
    BASE_URL + f"/api/networks/{user_network}/linked-apps", 
    params={"api_key": API_KEY}, 
    json={"access_token": user_token}
)
response_json = response.json()
assert response.status_code == 200
assert response_json["result"] == [user_app,]

# Deploy application
response = requests.put(
    BASE_URL + f"/api/deploy/{user_app}",
    params={"api_key": API_KEY, "repo_url": user_app_repo_url},
    json={"access_token": user_token}
)
assert response.status_code == 200

print("All tests passed successfully!")