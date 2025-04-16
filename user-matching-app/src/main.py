# main.py

import os
from flask import Flask, request, jsonify
from database.connection import connect_db  # Corrected import
from services.user_service import UserService
from services.matching_service import MatchingService
from api.gemini_api import GeminiAPI

app = Flask(__name__)

# Initialize database connection
db_connection = connect_db(os.getenv('DATABASE_URL'))  # Corrected function name
user_service = UserService(db_connection)
matching_service = MatchingService(user_service)
gemini_api = GeminiAPI()

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user_service.add_user(data)
    return jsonify({"message": "User added successfully!"}), 201

@app.route('/match_users', methods=['POST'])
def match_users():
    user_id = request.json.get('user_id')
    matches = matching_service.find_matches(user_id)
    return jsonify(matches), 200

if __name__ == '__main__':
    app.run(debug=True)