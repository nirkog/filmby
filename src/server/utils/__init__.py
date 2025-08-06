import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, content):
    # TODO: This function could be optimized (read password once...)

    with open(os.path.expanduser("~/email_password.txt"), "r") as f:
        password = f.read().strip()

    with open(os.path.expanduser("~/email_user.txt"), "r") as f:
        email = f.read().strip()

    host = "smtp.mailersend.net"
    to = "nirkog@gmail.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = email
    message["To"] = to

    part = MIMEText(content, "plain")
    message.attach(part)


    server = smtplib.SMTP(host, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email, password)
    server.sendmail(email, to, message.as_string())

    server.quit()
