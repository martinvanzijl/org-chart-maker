from flask import current_app as app
from flask_mail import Mail, Message

class MailServer:
    """Mail server."""

    def __init__(self):
        """Constructor."""

        self.setupMailEnvironment()

    def setupMailEnvironment(self):
        """Set up the mail environment."""

        # Set up email server details.
        # app.config['MAIL_SERVER'] ='smtp.gmail.com'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = 'yourId@gmail.com'
        # app.config['MAIL_PASSWORD'] = '*****'
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        app.config['MAIL_SERVER'] = 'localhost'
        app.config['MAIL_PORT'] = 25
        app.config['MAIL_USERNAME'] = 'org-chart-maker-user'
        app.config['MAIL_PASSWORD'] = 'org-chart-maker-password'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True

        # Create mail object.
        self.mail = Mail(app)

    def sendPasswordResetEmail(self):
        """Send an email to reset a user password."""

        # Send it.
        msg = Message('Hello', sender = 'yourId@gmail.com', recipients = ['someone1@gmail.com'])
        msg.body = "This is the email body"
        self.mail.send(msg)
