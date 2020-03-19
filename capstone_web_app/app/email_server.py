from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# Reads and returns template from specified text file
def read_template(filename):
    with open('email_templates/' + filename, 'r', encoding='utf-8') as template_file:
        content = template_file.read()
    return Template(content)


class Email(object):
    USERNAME = 'teamuntitledtech@gmail.com'
    PASSWORD = 'Bulldawgs2020'
    host_address = 'smtp.gmail.com'
    host_port = 587

    # Open connection to host server
    connection = smtplib.SMTP(host=host_address, port=host_port)
    connection.ehlo()

    def __init__(self, name, email):
        self.client = name
        self.client_email = email

        # Start tls connection with server and login
        self.connection.starttls()
        self.connection.login(self.USERNAME, self.PASSWORD)

    # Compiles a message that contains the from, to, subject, and body of an email
    def make_email_message(self, filename, subject, message=None):
        temp_msg = message
        if temp_msg is None:
            message_template = read_template(filename)

            # add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=self.client)

        msg = MIMEMultipart()  # create a message

        # setup the parameters of the message
        msg['From'] = self.USERNAME
        msg['To'] = self.client_email if temp_msg is None else self.USERNAME
        msg['Subject'] = subject

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        return msg

    # Sends verification email to client
    def send_verification(self):
        msg = self.make_email_message('verification_email.txt', subject='Stargazer Email Verification')
        self.connection.send_message(msg)
        del msg
        self.connection.quit()

    # Sends notification email to client
    def send_notification(self):
        msg = self.make_email_message('notification_email.txt', subject='Stargazer Notification')
        self.connection.send_message(msg)
        del msg
        self.connection.quit()

    # Sends customer message from contact us page to our email
    def send_customer_email(self, message):
        subject = 'Message from ' + self.client + ' (' + self.client_email + ')'
        msg = self.make_email_message('support_email.txt', subject=subject, message=message)
        self.connection.send_message(msg)
        del msg
        self.connection.quit()


# Testing code
if __name__ == "__main__":
    client_email = Email('Alex', 'afaucheux78@gmail.com')
    client_email.send_customer_email("HELLO")
