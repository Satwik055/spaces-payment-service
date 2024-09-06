from flask import Flask, jsonify, request
import psycopg2


DB_CONFIG = {
    'host': "aws-0-ap-south-1.pooler.supabase.com",
    'database': "postgres",
    'user': "postgres.fayafjrwupqupjltsdeg",
    'password': "@Satwikkr055"
}

connection = psycopg2.connect(**DB_CONFIG)
cursor = connection.cursor()
app = Flask(__name__)

@app.route("/hello", methods=['GET'])
def hello():
    return "Hello from payment service"


if __name__ == '__main__':
    app.run()