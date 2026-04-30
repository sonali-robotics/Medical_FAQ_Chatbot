import json
import os
import bcrypt

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(username, password, confirm_password):
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if password != confirm_password:
        return False, "Passwords do not match."

    users = load_users()
    if username in users:
        return False, "Username already exists. Please choose another."

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users[username] = hashed.decode("utf-8")
    save_users(users)
    return True, "Account created successfully! Please log in."

def login(username, password):
    if not username or not password:
        return False, "Please enter username and password."

    users = load_users()
    if username not in users:
        return False, "Username not found."

    stored_hash = users[username].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return True, "Login successful!"
    else:
        return False, "Incorrect password."