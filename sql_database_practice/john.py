import psycopg2
from flask import Flask, request, jsonify

conn = psycopg2.connect("dbname='john'")
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
         active smallint 
      );
   """)
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint 
      );
   """)
   print("Creating tables...")
   conn.commit()



app = Flask(__name__)


@app.route('/user/add', methods=['POST'])
def user_add():
    post_data = request.form if request.form else request.json()
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    cursor.execute("INSERT INTO Users (first_name, last_name, email, phone, city, state, org_id, active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", [first_name, last_name, email, phone, city, state, org_id, active])
    
    return jsonify("User created"), 201


@app.route('/users', methods=["GET"])
def get_all_active_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE active = 1;")
    results = cursor.fetchall()
    if not results:
        return jsonify("No Users in Table"), 404
    else:
        results_list = []
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
            results_list.append(results_dict)
        return jsonify(results_list), 200
if __name__=="__main__":
    create_all()
    app.run(port="8089", host="0.0.0.0", debug=True)

@app.route('/user/<id>', methods=["GET"])
def get_user_by_id(id):
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id=(%s);", [id])
    result = cursor.fetchone()
    if not result:
        return jsonify(f"No Users with id of {id}"), 404
    else:
        result_dict ={
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
        return jsonify(result_dict), 200


@app.route('/user/update/<id>', methods=["PUT"])
def user_update(id):

    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id = %s", [id])
    result = cursor.fetchone()
    if not result:
        return jsonify("User not in Database"), 404
   
    post_data = request.form if request.form else request.json()

    first_name = post_data.get('first_name')
    if not first_name:
        first_name = result[1]
    last_name = post_data.get('last_name')
    if not last_name:
        last_name = result[2]
    email = post_data.get('email')
    if not email:
        email = result[3]
    phone = post_data.get('phone')
    if not phone:
        phone = result[4]
    city = post_data.get('city')
    if not city:
        city = result[5]
    state = post_data.get('state')
    if not state:
        state = result[6]
    org_id = post_data.get('org_id')
    if not org_id:
        org_id = result[7]
    active = post_data.get('active')
    if not active:
        active = result[8]

    cursor.execute("UPDATE Users SET first_name=(%s), last_name=(%s), email=(%s), phone=(%s), city=(%s), state=(%s), org_id=(%s), active=(%s)"
    "WHERE user_id=(%s)", (first_name, last_name, email, phone, city, state, org_id, active, id )
    )

    return jsonify("User updated")
if __name__=="__main__":
    create_all()
    app.run(port="8089", host="0.0.0.0", debug=True)