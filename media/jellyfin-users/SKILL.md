---
name: jellyfin-users
description: Retrieve and list users configured in a Jellyfin instance.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [Jellyfin, media, users, API, database]
---

# Jellyfin Users

## Description
Retrieve and list users configured in a Jellyfin instance. This skill provides a method to fetch user information from the Jellyfin API or database.

## Prerequisites
- Jellyfin server running and accessible
- API endpoint URL
- Appropriate permissions to access Jellyfin logs and database

## Steps
1. **Determine Jellyfin API URL**: Ensure the Jellyfin server is running and accessible on the correct port.
2. **Access API**: Use the correct endpoint to fetch user information.
3. **List Users**: Retrieve and display the list of users.

## Usage
### Check Jellyfin Process
```bash
ps aux | grep jellyfin
```

### Check Ports
```bash
netstat -tulnp | grep jellyfin
```

### Access API
```bash
curl -s http://localhost:<PORT>/api/users -H "Accept: application/json"
```

## Jellyfin API Endpoints
- **Users**: `GET /api/users`

## Example Code
```python
import requests
import json

# Define the Jellyfin server URL and port
jellyfin_url = "http://<LAN_IP>"
jellyfin_port = 8123  # Your Jellyfin instance port

# Define the API endpoint for users
users_endpoint = f"{jellyfin_url}:{jellyfin_port}/api/users"

# Headers for the request
headers = {
    "Accept": "application/json"
}

# Fetch the list of users
try:
    response = requests.get(users_endpoint, headers=headers)
    response.raise_for_status()
    users = response.json()
    
    print("Users in Jellyfin:")
    for user in users:
        print(f"- {user.get('Name', 'Unknown')}")
        
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch users via API: {e}")
    
    # Fallback: Check logs
    print("\nFallback: Checking logs...")
    
    # Use SQLite to inspect the Users table
    print("\nChecking database...")

    # Check if jellyfin user exists and has access
    import pwd
    import grp
    
    try:
        jellyfin_uid = pwd.getpwnam("jellyfin").pw_uid
        jellyfin_gid = grp.getgrnam("jellyfin").gr_gid
        print(f"Jellyfin user exists with UID: {jellyfin_uid}, GID: {jellyfin_gid}")
    except KeyError:
        print("Jellyfin user not found on system")
        jellyfin_uid = None

    # Use SQLite to inspect the Users table
    import sqlite3
    db_path = "/home/alticcio/.local/share/jellyfin-server/data/Jellyfin.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users';")
        tables = cursor.fetchall()
        
        if tables:
            print("Users table exists. Fetching user names...")
            cursor.execute("SELECT Name, Id FROM Users;")
            users = cursor.fetchall()
            print("\nUsers in the Jellyfin database:")
            for user in users:
                print(f"  - {user[0]} (ID: {user[1]})")
        else:
            print("Users table not found in the database.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
```

## Database Access
Jellyfin uses SQLite for its database. The database file is typically located at:

```bash
/var/lib/jellyfin/database/Jellyfin.db
```

You can use SQLite tools to inspect the database:
```bash
sqlite3 /var/lib/jellyfin/database/Jellyfin.db ".schema Users"
```

## Notes
- Ensure you have permissions to access the Jellyfin server and database.
- If the API is not accessible, check the Jellyfin logs for errors.

## Troubleshooting
- **Connection Issues**: Ensure Jellyfin is running and the port is correct.
- **Authentication**: If authentication is required, include the appropriate headers or tokens.
- **Permissions**: Ensure you have read access to the Jellyfin database and logs.