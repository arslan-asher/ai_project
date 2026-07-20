# DO NOT USE IN PRODUCTION - TEST CODE FOR AI BOT
API_SECRET_KEY = "AIzaSyD-FAKE_KEY_1234567890"  # Hardcoded secret leak

def execute_user_query(db_connection, user_input):
    # Unsafe SQL injection flaw
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    return db_connection.execute(query)