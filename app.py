from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key ='InternA7coder'
# MySQL connection configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Enter Password",
    # database="auth"
)

# Create the users table if it doesn't exist
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS auth")
cursor.execute("USE auth")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password VARCHAR(255)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        id VARCHAR(50),
        order_date DATE,
        company VARCHAR(50),
        owner VARCHAR(50),
        item VARCHAR(50),
        quantity INT,
        weight FLOAT,
        request_shipment VARCHAR(100),
        tracking_id VARCHAR(50) UNIQUE,
        shipment_size VARCHAR(50),
        box_count INT,
        specification VARCHAR(100),
        checklist_quantity VARCHAR(50)
        
    )
""")

dummy_users = [
    ("admin", generate_password_hash("password")),
    ("customer1", generate_password_hash("password")),
    ("customer2", generate_password_hash("password"))
]

for user in dummy_users:
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", user)

db.commit()



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Fetch user input
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the records
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            # Successful login, redirect to the appropriate form
            session['user_id'] = username
            if username in ['customer1', 'customer2']:
                return redirect('/order')
            elif username =='admin':
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            # Invalid credentials, display an error message
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/order', methods=['GET', 'POST'])
def customer_form():
    if 'user_id' not in session:
        return redirect('/login')
    else:
        try:
            if request.method == 'POST':
                
                # Fetch form data
                id = session['user_id']
                order_date = request.form['order_date']
                company = request.form['company']
                owner = request.form['owner']
                item = request.form['item']
                quantity = int(request.form['quantity'])
                weight = float(request.form['weight'])
                request_shipment = request.form['request_shipment']
                tracking_id = request.form['tracking_id']
                shipment_size = request.form['shipment_size']
                box_count = int(request.form['box_count'])
                specification = request.form['specification']
                checklist_quantity = request.form['checklist_quantity']

                # Store form data in the customer table
                cursor = db.cursor()
                insert_query = """
                    INSERT INTO customer (
                        id,order_date, company, owner, item, quantity, weight,
                        request_shipment, tracking_id, shipment_size, box_count,
                        specification, checklist_quantity
                    )
                    VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data = (
                    id,order_date, company, owner, item, quantity, weight,
                    request_shipment, tracking_id, shipment_size, box_count,
                    specification, checklist_quantity
                )
                cursor.execute(insert_query, data)
                db.commit()

                return redirect('/order')

            return render_template('order.html')
        except:
            return ("Duplicate Tracking Id")

@app.route('/admin')
def data():

    # Check if the user is logged in as admin
    if  'user_id' in session and session['user_id'] == 'admin':
        
        try:
            # Retrieve data from the customer table
            cursor = db.cursor()
            cursor.execute("""
                SELECT SUM(quantity), SUM(weight), SUM(box_count) FROM customer WHERE id = 'customer1'   """)
            data1 = cursor.fetchone()

            cursor.execute("""
                SELECT SUM(quantity), SUM(weight), SUM(box_count) FROM customer WHERE id = 'customer2'    """)
            data2 = cursor.fetchone()
        
            total_quantity = data1[0] + data2[0]
            total_weight = data1[1] + data2[1]
            total_box_count = data1[2] + data2[2]
            print(total_box_count,total_quantity,total_weight)
    
            return render_template('admin.html', data1=data1,data2=data2, total_quantity=total_quantity, total_weight=total_weight, total_box_count=total_box_count)
        except:
            return 'No Data Found'
    return redirect('/login')



@app.route('/')
def home():
    return "Welcome to the home page!"

if __name__ == '__main__':
    app.run()
