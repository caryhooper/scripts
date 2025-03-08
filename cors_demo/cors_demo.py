from flask import Flask, request, make_response, jsonify
import json
import os
from threading import Thread

# Fake HR data template
FAKE_HR_DATA = [
    {
        "employee_id": "EMP001",
        "name": "John Smith",
        "address": "123 Maple St, Springfield, IL 62701",
        "pay": 65000.00,
        "work_phone": "(217) 555-0100",
        "email": "john.smith@fakecompany.com",
        "bank_account": "1234567890",
        "ssn": "123-45-6789"
    },
    {
        "employee_id": "EMP002",
        "name": "Jane Doe",
        "address": "456 Oak Ave, Springfield, IL 62702",
        "pay": 72000.00,
        "work_phone": "(217) 555-0200",
        "email": "jane.doe@fakecompany.com",
        "bank_account": "2345678901",
        "ssn": "234-56-7890"
    },
    {
        "employee_id": "EMP003",
        "name": "Bob Johnson",
        "address": "789 Pine Rd, Springfield, IL 62703",
        "pay": 58000.00,
        "work_phone": "(217) 555-0300",
        "email": "bob.johnson@fakecompany.com",
        "bank_account": "3456789012",
        "ssn": "345-67-8901"
    },
    {
        "employee_id": "EMP004",
        "name": "Alice Brown",
        "address": "321 Elm St, Springfield, IL 62704",
        "pay": 85000.00,
        "work_phone": "(217) 555-0400",
        "email": "alice.brown@fakecompany.com",
        "bank_account": "4567890123",
        "ssn": "456-78-9012"
    },
    {
        "employee_id": "EMP005",
        "name": "Mike Wilson",
        "address": "654 Cedar Ln, Springfield, IL 62705",
        "pay": 62000.00,
        "work_phone": "(217) 555-0500",
        "email": "mike.wilson@fakecompany.com",
        "bank_account": "5678901234",
        "ssn": "567-89-0123"
    }
]

# Create data file if it doesn't exist
DATA_FILE = "hr_data.json"
ATTACKER_DATA_FILE = "attacker_data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump(FAKE_HR_DATA, f, indent=2)

# Function to load HR data from file
def load_hr_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Create Flask apps
app3000 = Flask(__name__)
app8000 = Flask(__name__)
app2000 = Flask(__name__)

# Common function to format data into HTML
def format_hr_data(data):
    rows = ""
    for record in data:
        rows += "<tr>"
        rows += f"<td>{record['employee_id']}</td>"
        rows += f"<td>{record['name']}</td>"
        rows += f"<td>{record['address']}</td>"
        rows += f"<td>${record['pay']:,.2f}</td>"
        rows += f"<td>{record['work_phone']}</td>"
        rows += f"<td>{record['email']}</td>"
        rows += f"<td>{record['bank_account']}</td>"
        rows += f"<td>{record['ssn']}</td>"
        rows += "</tr>"
    # HTML template for displaying HR data
    HTML_TEMPLATE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Data</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <h1>HR Data</h1>
        <table>
            <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Address</th>
                <th>Pay</th>
                <th>Work Phone</th>
                <th>Email</th>
                <th>Bank Account</th>
                <th>SSN</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return HTML_TEMPLATE

def format_data(data):
    rows = ""
    for record in data:
        rows += "<tr>"
        rows += f"<td>{record.get('employee_id', '')}</td>"
        rows += f"<td>{record.get('name', '')}</td>"
        rows += f"<td>{record.get('address', '')}</td>"
        rows += f"<td>{record.get('pay', '')}</td>"
        rows += f"<td>{record.get('work_phone', '')}</td>"
        rows += f"<td>{record.get('email', '')}</td>"
        rows += f"<td>{record.get('bank_account', '')}</td>"
        rows += f"<td>{record.get('ssn', '')}</td>"
        rows += "</tr>"
        # HTML template for displaying data
    HTML_TEMPLATE = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exfiltrated HR Data</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <h1>Exfiltrated HR Data</h1>
        <table>
            <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Address</th>
                <th>Pay</th>
                <th>Work Phone</th>
                <th>Email</th>
                <th>Bank Account</th>
                <th>SSN</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>"""
    return HTML_TEMPLATE

# Function to load existing data from file
def load_data():
    if not os.path.exists(ATTACKER_DATA_FILE):
        return []
    with open(ATTACKER_DATA_FILE, 'r') as f:
        return json.load(f)

# Function to save data to file
def save_data(data):
    with open(ATTACKER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Function to deduplicate data based on SSN
def dedupe_data(existing_data, new_data):
    # Create a dictionary with SSN as key for quick lookup
    data_dict = {record['ssn']: record for record in existing_data}
    
    # Update with new data (new records overwrite old ones if SSN matches)
    for record in new_data:
        data_dict[record['ssn']] = record
    
    # Convert back to list
    return list(data_dict.values())

@app2000.route('/exfil', methods=['GET', 'POST', 'OPTIONS'])
def exfil():
    origin = request.headers.get('Origin', '*')
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    # Handle GET request
    if request.method == 'GET':
        data = load_data()
        resp = make_response(format_data(data))
        resp.headers['Access-Control-Allow-Origin'] = origin
        return resp

    # Handle POST request
    if request.method == 'POST':
        try:
            new_data = request.get_json()
            if not new_data or not isinstance(new_data, list):
                return make_response('Invalid JSON data', 400)
            
            # Load existing data and deduplicate
            existing_data = load_data()
            updated_data = dedupe_data(existing_data, new_data)
            
            # Save updated data
            save_data(updated_data)
            
            resp = make_response('Data received and stored', 200)
            resp.headers['Access-Control-Allow-Origin'] = origin
            return resp
        except Exception as e:
            return make_response(f'Error processing data: {str(e)}', 500)

@app3000.route('/auto_login',methods=['GET'])
def hr_data_3000_login():
    # Set cookie 
    resp = make_response("<html><h1>Success!</h1></html>")
    resp.set_cookie('auth', 'super_secret_token', path='/', domain="adsftest.piedpiper.com",samesite="None",secure=True)
    origin = request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return resp

# Port 80 server (cookie-based auth)
@app3000.route('/hr_data', methods=['GET', 'OPTIONS'])
def hr_data_3000():
    origin = request.headers.get('Origin', '*')
    
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return resp

    resp = make_response()
    
    # Check cookie
    if request.cookies.get('auth') != 'super_secret_token':
        resp = make_response('Unauthorized', 403)
    else:
        data = load_hr_data()
        resp = make_response(format_hr_data(data))
    
    resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

# Port 8000 server (header-based auth)
@app8000.route('/hr_data', methods=['GET', 'OPTIONS'])
def hr_data_8000():
    origin = request.headers.get('Origin', '*')
    
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        #TODO - toggle this for successful attack.  The absence of this should prevent the attack.
        # resp.headers['Access-Control-Allow-Headers'] = 'X-Custom-Auth-Header'
        return resp

    # Check custom header
    auth_header = request.headers.get('X-Custom-Auth-Header')
    if auth_header != 'super_secret_token':
        cookie = request.cookies.get('auth')
        if cookie == "super_secret_token":
            resp = make_response(f'Observed "auth" cookie: {cookie}.  Please send in a header X-Custom-Auth-Header to retrieve the info.', 403)
        else:
            resp = make_response('Forbidden', 403)

    else:
        data = load_hr_data()
        resp = make_response(format_hr_data(data))
    
    resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Headers'] = 'X-Custom-Auth-Header'
    return resp

# Port 8000 server (header-based auth)
@app2000.route('/', methods=['GET', 'OPTIONS'])
def attacksite():
    html = """<html><h1>Attacker-Controlled Site</h1>
    <h4>This is an untrusted site which will be used to make HTTP requests to the vulnerable server.</h4></html>"""
    resp = make_response(html)
    return resp

# Function to run Flask app
def run_app(app, port):
    app.run(host='0.0.0.0', 
            port=port, 
            debug=False,
            ssl_context=('server.crt','server.key')
            )

if __name__ == '__main__':
    # Start both servers in separate threads
    t1 = Thread(target=run_app, args=(app3000, 3000))
    t2 = Thread(target=run_app, args=(app8000, 8000))
    t3 = Thread(target=run_app, args=(app2000, 2000))
    
    import time
    t1.start()
    time.sleep(2)
    t2.start()
    time.sleep(2)
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()

