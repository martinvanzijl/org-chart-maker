from flask import current_app as app
from flask_mail import Mail, Message

# Test.
import smtplib, ssl

class MailServer:
    """Mail server."""

    MESSAGE_BODY = "Here is your password reset link for Org Chart Maker:"
    RECEIVER_TEST = "martin.vanzijl@gmail.com"
    SENDER = "org-chart-maker@martinvz.com"
    SUBJECT = "Org Chart Maker - Password Reset Link"

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

        # Localhost test.
        # app.config['MAIL_SERVER'] = 'localhost'
        # app.config['MAIL_PORT'] = 25
        # app.config['MAIL_USERNAME'] = 'org-chart-maker-user'
        # app.config['MAIL_PASSWORD'] = 'org-chart-maker-password'
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        # Bluehost test #1.
        # app.config['MAIL_SERVER'] = 'martinvz.com'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = 'org-chart-maker'
        # app.config['MAIL_PASSWORD'] = ''
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        # Bluehost test #2.
        # app.config['MAIL_SERVER'] = "ssl://smtp.bluehost.com"
        app.config['MAIL_SERVER'] = "smtp.bluehost.com"
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = self.SENDER
        app.config['MAIL_PASSWORD'] = ''
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True

        # Create mail object.
        self.mail = Mail(app)

    def sendPasswordResetEmail(self):
        """Send an email to reset a user password."""

        # Send it.
        msg = Message(self.SUBJECT, sender = self.SENDER, recipients = [self.RECEIVER_TEST])
        msg.body = self.MESSAGE_BODY
        self.mail.send(msg)

        # TLS test.
        # port = 587 # For starttls
        # port = 25  # For starttls
        # smtp_server = "localhost"
        # sender_email = "org-chart-maker@martinvz.com"
        # receiver_email = "martin.vanzijl@gmail.com"
        # password = input("org-chart-maker-password")
        # message = """\
        # Subject: Hi there
        #
        # This message is sent from Python."""
        #
        # context = ssl.create_default_context()
        # with smtplib.SMTP(smtp_server, port) as server:
        #     server.ehlo()  # Can be omitted
        #     server.starttls(context=context)
        #     server.ehlo()  # Can be omitted
        #     server.login(sender_email, password)
        #     server.sendmail(sender_email, receiver_email, message)
