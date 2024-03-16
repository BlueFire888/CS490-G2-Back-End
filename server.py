from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS 
from shapely.geometry import Point

app = Flask(__name__)
CORS(app) 

HOST = "localhost"
USER = "root"
PASSWORD = "!@Jff05288"
DB = "CS490"


@app.route("/inventoryInStock")
def movies():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    with db.cursor() as cursor:
        sql = """Select *
                FROM inventory
                WHERE status = %s;"""
        cursor.execute(sql, ('InStock'))
        results = cursor.fetchall()
        if not results:
            return jsonify({"inStockInventory": []})
        return jsonify({"inStockInventory": results})
    



@app.route("/addUser", methods=['POST'])
def addCustomer():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    job = data.get('job')
    password = data.get('password')

    user_id = 0
    job_id = 0

    # Check if email already exists
    with db.cursor() as cursor:
        query = """SELECT * 
                    FROM authentication WHERE email = %s"""
        cursor.execute(query, ([email]))
        results = cursor.fetchall()
        if results:
            response = {
                'message': 'Email Already Exists'
            }
            return jsonify(response), 200
        
    # Check if username already exists
    with db.cursor() as cursor:
        query = """SELECT * 
                    FROM authentication WHERE username = %s"""
        cursor.execute(query, ([username]))
        results = cursor.fetchall()
        if results:
            response = {
                'message': 'Username Already Exists'
            }
            return jsonify(response), 200

    # get job_id
    with db.cursor() as cursor:
        query = "SELECT * FROM jobs WHERE job_title = %s"
        cursor.execute(query, ([job]))
        results = cursor.fetchall()
        job_id = results[0][1]

    # insert into users
    with db.cursor() as cursor:
        query = """
                INSERT INTO users (job_id, phone_number, first_name, last_name, insert_date, update_date) VALUES 
                                    (%s, %s, %s, %s, NOW(), NOW())
                """
        cursor.execute(query, (job_id, phone_number, first_name, last_name))
        db.commit()
        
    # insert into authentication
    with db.cursor() as cursor:
        query = "SELECT * FROM users WHERE phone_number = %s"
        cursor.execute(query, ([phone_number]))
        results = cursor.fetchall()
        user_id = results[0][0]

        query = """
                INSERT INTO authentication (user_id, username, email, password, insert_date, update_date) VALUES 
                                    (%s, %s, %s, %s, NOW(), NOW())
                """
        cursor.execute(query, (user_id, username, email, password))
        db.commit()

    response = {
        'message': 'User added successfully'
    }
    return jsonify(response), 200




@app.route("/authenticate", methods=['POST'])
def addCustomer():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_id = 0
    job_id = 0

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """SELECT * 
                    FROM authentication WHERE username = %s AND password = %s"""
        cursor.execute(query, ([username], [password]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Incorrect username or password'
            }
            return jsonify(response), 200

    response = {
        'message': 'Authentication successful'
    }
    return jsonify(response), 200



    

if __name__ == "__main__":
    app.run(debug=True)
