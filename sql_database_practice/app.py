import psycopg2
from flask import Flask, request, jsonify

conn = psycopg2.connect("dbname='UsersDB'")
cursor = conn.cursor()

def create_all():
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint DEFAULT 0
      );
   """)
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint DEFAULT 0
      );
   """)
   print("Creating tables...")
   conn.commit()

create_all()

app = Flask(__name__)

@app.route('/user/add', methods=['POST'])
def user_add():

    post_data = request.form if request.form else request.get_json()


    first_name = post_data.get('first_name')
    if not first_name:
        return jsonify("First Name is Required"), 400
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    if not email:
        return jsonify("Email is required and Unique"), 400
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    cursor.execute("INSERT INTO Users (first_name, last_name, email, phone, city, state, org_id, active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", [first_name, last_name, email, phone, city, state, org_id, active])
    conn.commit()
    return jsonify("User created",post_data), 201

@app.route('/user/get', methods=["GET"])
def get_all_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users")
    results = cursor.fetchall()
    if not results:
        return jsonify("No Users in Database"), 404
    
    end_results = []
    for result in results:
        results_dict ={
            'user_id': result[0],
            'first_name': result[1],
            'last_name': result[2],
            'email': result[3],
            'phone': result[4],
            'city': result[5],
            'state': result[6],
            'org_id': result[7],
            'active': result[8]
        }
        end_results.append(results_dict)
    return jsonify(end_results)

@app.route('/user/update/<id>', methods=["PATCH"])
def user_update(id):
    post_data = request.form if request.form else request.get_json()

    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    cursor.execute("UPDATE Users SET first_name=(%s), last_name=(%s), email=(%s), phone=(%s), city=(%s), state=(%s), org_id=(%s), active=(%s)"
    "WHERE user_id=(%s)", (first_name, last_name, email, phone, city, state, org_id, active, id )
    )

    

if __name__=="__main__":
    app.run(port="8089", host="0.0.0.0")
