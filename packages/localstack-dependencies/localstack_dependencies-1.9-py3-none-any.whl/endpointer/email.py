import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import ssl

def send_plain_email(sender_name, sender_email, email_server_user, email_server_password, receiver_email, subject, body, smtp_server, smtp_port):
    
    message = MIMEText(body, "plain")
    message["From"] = formataddr((sender_name, sender_email))
    message["To"] = receiver_email
    message["Subject"] = subject

    context = ssl.create_default_context()

    try:
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()
            
            server.login(email_server_user, email_server_password)
            
            server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        raise
