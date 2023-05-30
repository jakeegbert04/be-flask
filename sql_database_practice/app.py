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


@app.route('/user/get/<id>', methods=["GET"])
def get_user_by_id(id):
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM Users WHERE user_id = %s", [id])
    result = cursor.fetchone()
    if not result:
        return jsonify("User not in Database"), 404
    result_dict ={
        "user_id": result[0],
        "first_name": result[1],
        "last_name": result[2],
        "email": result[3],
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
   
    post_data = request.form if request.form else request.get_json()

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

@app.route('/user/deactivate/<id>', methods=["PATCH"])
def deactivate_user(id):
    cursor.execute("UPDATE Users SET active=(0) WHERE user_id=(%s)", [id])
    conn.commit()

    return jsonify("user deactivated")

@app.route('/user/activate/<id>', methods=["PATCH"])
def activate_user(id):
    cursor.execute("UPDATE Users SET active=(1) WHERE user_id=(%s)", [id])
    conn.commit()

    return jsonify("user activated")

@app.route('/user/delete/<id>', methods=["DELETE"])
def delete_user(id):
    cursor.execute("DELETE FROM Users WHERE user_id=(%s)", [id])
    conn.commit()

    return jsonify(f"User {id} was deleted")


@app.route('/org/add', methods=['POST'])
def org_add():

    post_data = request.form if request.form else request.get_json()


    name = post_data.get('name')
    if not name:
        return jsonify("Name is Required"), 400
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    active = post_data.get('active')

    cursor.execute("INSERT INTO Organizations (name, phone, city, state, active) VALUES (%s, %s, %s, %s, %s);", [name, phone, city, state, active])
    conn.commit()
    return jsonify("Organization created",post_data), 201


@app.route('/org/update/<id>', methods=["PUT"])
def update_org_by_id(id):
    cursor.execute(
        "SELECT org_id, name, phone, city, state, active FROM Organizations WHERE org_id =%s;",
        [id])
    result = cursor.fetchone()

    if not result:
        return jsonify('That org does not exist'), 404
    else:

        result_dict = {
            "org_id": result[0],
            "name": result[1],
            "phone": result[2],
            "city": result[3],
            "state": result[4],
            "active": result[5]
        }

    post_data = request.form if request.form else request.json

    for key, val in post_data.copy().items():
        if not val:
            post_data.pop(key)

    result_dict.update(post_data)

    cursor.execute(
        '''UPDATE Organizations SET 
        name = %s,   
        phone= %s, 
        city= %s, 
        state= %s, 
        active= %s 
        
        WHERE org_id = %s
    ;''',
        [
         result_dict['name'],
         result_dict["phone"],
         result_dict["city"],
         result_dict['state'],
         result_dict['active'],
         result_dict["org_id"]
         ])
    conn.commit()
    return jsonify('org updated')


@app.route('/org/get', methods=["GET"])
def get_all_orgs():
    cursor.execute("SELECT org_id, name, phone, city, state, active FROM Organizations")
    results = cursor.fetchall()
    if not results:
        return jsonify("No orgs in Database"), 404
    
    end_results = []
    for result in results:
        results_dict ={
            'org_id': result[0],
            'name': result[1],
            'phone': result[2],
            'city': result[3],
            'state': result[4],
            'active': result[5]
        }
        end_results.append(results_dict)
    return jsonify(end_results)


@app.route('/org/get/<id>', methods=["GET"])
def get_org_by_id(id):
    cursor.execute("SELECT org_id, name, phone, city, state, active FROM Organizations WHERE org_id = %s", [id])
    result = cursor.fetchone()
    if not result:
        return jsonify("Org not in Database"), 404
    result_dict ={
        "org_id": result[0],
        "name": result[1],
        'phone': result[2],
        'city': result[3],
        'state': result[4],
        'active': result[5]

    }
    return jsonify(result_dict), 200


@app.route('/org/activate/<id>', methods=["PATCH"])
def activate_org(id):
    cursor.execute("UPDATE Organizations SET active=(1) WHERE org_id=(%s)", [id])
    conn.commit()

    return jsonify("org activated")

@app.route('/org/deactivate/<id>', methods=["PATCH"])
def deactivate_org(id):
    cursor.execute("UPDATE Organizations SET active=(0) WHERE org_id=(%s)", [id])
    conn.commit()

    return jsonify("org deactivated")

@app.route('/org/delete/<id>', methods=["DELETE"])
def delete_org(id):
    cursor.execute("DELETE FROM Organizations WHERE org_id=(%s)", [id])
    conn.commit()

    return jsonify(f"Org {id} was deleted")
    

if __name__=="__main__":
    app.run(port="8089", host="0.0.0.0", debug=True)
