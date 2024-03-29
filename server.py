from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS 
from shapely.geometry import Point

app = Flask(__name__)
CORS(app)

HOST = "localhost"
USER = "root"
PASSWORD = ""
DB = "CS490"


@app.route("/inventoryInStock", methods=['GET'])
def inventoryInStock():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    with db.cursor() as cursor:
        sql = """Select i.vin, c.make, c.model, c.year,
                        cd.price, cd.exterior_color, cd.interior_color, 
                        cd.wheel_drive, cd.mileage, cd.transmission, cd.seats
                FROM inventory i
                    LEFT JOIN cars c on c.car_id = i.car_id
                    LEFT JOIN car_details cd on cd.vin = i.vin
                WHERE status = %s;"""
        cursor.execute(sql, ('InStock'))
        results = cursor.fetchall()
        if not results:
            return jsonify({"inStockInventory": []})
        return jsonify({"inStockInventory": results})
    


@app.route("/carDetails", methods=['POST'])
def carDetails():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    carID = data.get('carID')
    with db.cursor() as cursor:
        sql = """Select i.vin, c.make, c.model, c.year,
                        cd.price, cd.exterior_color, cd.interior_color, 
                        cd.wheel_drive, cd.mileage, cd.transmission, cd.seats
                FROM inventory i
                    LEFT JOIN cars c on c.car_id = i.car_id
                    LEFT JOIN car_details cd on cd.vin = i.vin
                WHERE car_id = %s;"""
        cursor.execute(sql, ([carID]))
        results = cursor.fetchall()
        if not results:
            return jsonify({"carDetails": []})
        return jsonify({"carDetails": results})
    


@app.route("/userInfo", methods=['POST'])
def userInfo():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    userID = data.get('userID')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """SELECT u.user_id, j.job_title, u.phone_number, u.first_name, u.last_name, a.username, a.email
                    FROM users u
                        LEFT JOIN jobs j on j.job_id = u.job_id
                        LEFT JOIN authentication a on a.user_id = u.user_id
                    WHERE u.user_id = %s"""
        cursor.execute(query, ([userID]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving customer'
            }
            return jsonify(response), 200

    return jsonify({"inStockInventory": results})




@app.route("/addUser", methods=['POST'])
def addUser():
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
        
    # Check if phone number already exists
    with db.cursor() as cursor:
        query = """SELECT * 
                    FROM users WHERE phone_number = %s"""
        cursor.execute(query, ([phone_number]))
        results = cursor.fetchall()
        if results:
            response = {
                'message': 'Phone Number Already Exists'
            }
            return jsonify(response), 200

    # get job_id
    with db.cursor() as cursor:
        query = "SELECT * FROM jobs WHERE job_title = %s"
        cursor.execute(query, ([job]))
        results = cursor.fetchall()
        print("RESULTS: ", results, " AND I THINK JOB_ID IS: ", results[0][0])
        job_id = results[0][0]

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
def authenticate():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

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



@app.route("/myGarageInv", methods=['GET'])
def myGarageInv():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    with db.cursor() as cursor:
        sql = """Select g.cust_id, g.vin, c.make, c.model, c.year
                FROM myGarage g
                    LEFT JOIN cars c on c.car_id = g.car_id;"""
        cursor.execute(sql, )
        results = cursor.fetchall()
        if not results:
            return jsonify({"myGarageInv": []})
        return jsonify({"myGarageInv": results})

    

@app.route("/myGarageAddCar", methods=['POST'])
def myGarageAddCar():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    custID = data.get('custID')
    make = data.get('make')
    model = data.get('model')
    year = data.get('year')
    vin = data.get('vin')

    with db.cursor() as cursor:
        query = """SELECT car_id
                    FROM cars WHERE make = %s AND model = %s AND year = %s"""
        cursor.execute(query, ([make], [model], [year]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving car_id'
            }
            return jsonify(response), 200
        carID = results[0][0]

        query = """
                INSERT INTO myGarage (cust_id, vin, car_id, insert_date, update_date) VALUES 
                                    (%s, %s, %s, NOW(), NOW())
                """
        cursor.execute(query, (custID, vin, carID))
        db.commit()

    response = {
        'message': 'Car Added to My Garage'
    }
    return jsonify(response), 200



@app.route("/carPurchaseHistory", methods=['POST'])
def carPurchaseHistory():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    userID = data.get('userID')

    with db.cursor() as cursor:
        query = """SELECT c.make, c.model, c.year, cs.vin, cs.insert_date, n.price, 
                    FROM users u
                        LEFT JOIN car_sales cs on cs.user_id = u.user_id
                        LEFT JOIN inventory i on i.vin = cs.vin
                        LEFT JOIN cars c on c.car_id = i.car_id
                        LEFT JOIN negotiation n on n.vin = cs.vin
                    WHERE u.user_id = %s"""
        cursor.execute(query, ([userID]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving customer car purchases'
            }
            return jsonify(response), 200

    return jsonify({"carPurchaseHistory": results})



@app.route("/productPurchaseHistory", methods=['POST'])
def productPurchaseHistory():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    userID = data.get('userID')

    with db.cursor() as cursor:
        query = """SELECT p.product_name, p.price, p.description, ps.insert_date
                    FROM users u
                        LEFT JOIN product_sales ps on ps.user_id = u.user_id
                        LEFT JOIN products p on p.product_id = ps.product_id
                    WHERE u.user_id = %s"""
        cursor.execute(query, ([userID]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving customer product purchases'
            }
            return jsonify(response), 200

    return jsonify({"productPurchaseHistory": results})




@app.route("/updateUserInfo", methods=['POST'])
def updateUserInfo():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    userID = data.get('userID')
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')

    with db.cursor() as cursor:
        query = """UPDATE users
                    SET first_name = %s, last_name = %s, phone_number = %s
                    WHERE user_id = %s """
        cursor.execute(query, ([firstName], [lastName], [phoneNumber], [userID]))
        db.commit()

        query = """UPDATE authentication
                    SET email = %s
                    WHERE user_id = %s """
        cursor.execute(query, ([email], [userID]))
        db.commit()


    response = {
        'message': 'Successfully updated Customer Information'
    }
    return jsonify(response), 200



@app.route("/addFavorite", methods=['POST'])
def addFavorite():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    custID = data.get('custID')
    make = data.get('make')
    model = data.get('model')
    year = data.get('year')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """SELECT car_id
                    FROM cars WHERE make = %s AND model = %s AND year = %s"""
        cursor.execute(query, ([make], [model], [year]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving car_id'
            }
            return jsonify(response), 200
        carID = results[0][0]

        query = """
                INSERT INTO favorites (user_id, car_id, insert_date, update_date) VALUES 
                                    (%s, %s, NOW(), NOW())
                """
        cursor.execute(query, (custID, carID))
        db.commit()

    response = {
        'message': 'Car added to Favorites'
    }
    return jsonify(response), 200



@app.route("/delFavorite", methods=['POST'])
def delFavorite():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    custID = data.get('custID')
    make = data.get('make')
    model = data.get('model')
    year = data.get('year')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """SELECT car_id
                    FROM cars WHERE make = %s AND model = %s AND year = %s"""
        cursor.execute(query, ([make], [model], [year]))
        results = cursor.fetchall()
        if not results:
            response = {
                'message': 'Error retrieving car_id'
            }
            return jsonify(response), 200
        carID = results[0][0]

        query = """
                DELETE FROM favorites WHERE user_id = %s AND car_id = %s
                """
        cursor.execute(query, (custID, carID))
        db.commit()

    response = {
        'message': 'Car deleted from Favorites'
    }
    return jsonify(response), 200





@app.route("/checkCarInInv", methods=['POST'])
def checkCarInInv():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    vin = data.get('custID')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """SELECT *
                    FROM inventory WHERE vin = %s"""
        cursor.execute(query, ([vin]))
        results = cursor.fetchall()
    if not results:
        response = {
            'message': '0' #Car not found
        }
    else:
        response = {
            'message': '1' #Car found
        }
    return jsonify(response), 200




@app.route("/scheduleAppt", methods=['POST'])
def scheduleAppt():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    custID = data.get('custID')
    datetime = data.get('datetime')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """
                INSERT INTO test_drive_appointments (user_id, scheduled_date, status, site_id, insert_date, update_date)
                                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """
        cursor.execute(query, ([custID], [datetime], 'scheduled', [1]))
        db.commit()

    response = {
        'message': 'Appointment Scheduled'
    }
    return jsonify(response), 200



@app.route("/addCard", methods=['POST'])
def addCard():
    db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB)
    data = request.get_json()
    custID = data.get('custID')
    cardNum = data.get('cardNum')
    cardHolderName = data.get('cardHolderName')
    cvc = data.get('cvc')
    expDate = data.get('expDate')

    # Check if username and password is valid
    with db.cursor() as cursor:
        query = """
                INSERT INTO credit_card_history (user_id, cardholdername, number, sec_code, exp_date, insert_date, update_date)
                                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
        cursor.execute(query, ([custID], [cardHolderName], [cardNum], [cvc], [expDate]))
        db.commit()

    response = {
        'message': 'Card Added'
    }
    return jsonify(response), 200





if __name__ == "__main__":
    app.run(debug=True)
