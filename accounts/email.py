# accounts/email.py
import smtplib
import os

def send_otp_email(receiver_email, otp_code):
    """
    Send OTP email using direct SMTP.

    Args:
        receiver_email (str): Recipient's email address
        otp_code (str): The OTP code to send
    """
    email = os.getenv('EMAIL_HOST_USER')
    password = os.getenv('EMAIL_HOST_PASSWORD')
    subject = "OTP Verification"

    text = f"Subject: {subject}\n\nYour OTP code is: {otp_code}\n\nThis code will expire in 5 minutes."

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(email, receiver_email, text)
        print(f"OTP email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False
