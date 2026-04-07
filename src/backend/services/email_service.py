import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
        self.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        self.APP_PASSWORD = os.getenv("APP_PASSWORD")

    def send_email(self, recipient_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.EMAIL_ADDRESS
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.EMAIL_ADDRESS, self.APP_PASSWORD)
                server.sendmail(self.EMAIL_ADDRESS, recipient_email, msg.as_string())

            print("Email sent successfully")

        except Exception as e:
            print(f"Error sending the email: {e}")


if __name__ =="__main__":
    recipient = "jhlbolsonaro@gmail.com"
    subject = "Test Email"
    body = "this is a test email sent using python and gmail smtp."
    es = EmailService()
    es.send_email(recipient, subject, body)


