import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import filmby

DAY_NAMES = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]
VENUE_NAME_TRANSLATIONS = dict()

def get_day_name(date):
    try:
        return DAY_NAMES[date.weekday()]
    except Exception:
        return ""

def get_venue_name_translations():
    if len(VENUE_NAME_TRANSLATIONS) == 0:
        for venue in filmby.VENUES:
            VENUE_NAME_TRANSLATIONS[venue.NAME] = venue.TRANSLATED_NAMES["heb"]

    return VENUE_NAME_TRANSLATIONS

def send_email(subject, content):
    # TODO: This function could be optimized (read password once...)

    subject = "Filmby Alert - " + subject

    with open(os.path.expanduser("~/email_password.txt"), "r") as f:
        password = f.read().strip()

    with open(os.path.expanduser("~/email_user.txt"), "r") as f:
        email = f.read().strip()

    host = "smtp.gmail.com"
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
