import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(to_email, subject, body):
    # Set these with your Zoho email and app password
    sender_email = "convoshop@zohomail.com"
    sender_password = "gEFEJpaYu3zK"  # Use Zoho app password

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Replace with your test recipient email
    test_email = "m.huzaifarabbani@gmail.com"
    subject = "Test Email from ConvoShop"
    body = """
    <h3>This is a test email</h3>
    <p>If you received this, your Zoho email setup works!</p>
    """
    send_email_notification(test_email, subject, body)