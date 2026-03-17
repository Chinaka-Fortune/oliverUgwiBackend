import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, is_html=False):
    """
    Sends an email using standard SMTP.
    Requires SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD in env.
    """
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USERNAME')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    from_email = os.environ.get('MAIL_DEFAULT_SENDER', smtp_user)

    if not smtp_user or not smtp_pass:
        print("SMTP Credentials not configured. Assuming development mode.")
        print(f"[Email Mock] To: {to_email}")
        print(f"[Email Mock] Subject: {subject}")
        print(f"[Email Mock] Body:\n{body}")
        return True # Mock success in dev

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    if is_html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
