from .otp import generate_otp_secret, generate_otp, verify_otp
from .email import send_otp_email

def send_login_otp(request, email):
    secret = generate_otp_secret()
    otp = generate_otp(secret)

    request.session["otp_secret"] = secret
    request.session["otp_email"] = email

    success = send_otp_email(email, otp)
    if not success:
        # Email sending failed, but continue with OTP generation for development
        print(f"Warning: OTP email failed to send. OTP for {email} is {otp}")

def validate_otp(request, user_otp):
    secret = request.session.get("otp_secret")
    if not secret:
        return False
    return verify_otp(secret, user_otp)
