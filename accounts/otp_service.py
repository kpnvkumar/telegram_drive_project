from .otp import encrypt_random_integer, generate_otp, verify_otp
from .email import send_otp_email

def send_login_otp(request, email):
    _, _, secret, _ = encrypt_random_integer()
    otp = generate_otp(secret)

    request.session["otp_secret"] = secret
    request.session["otp_email"] = email

    success = send_otp_email(email, otp)
    if not success:
        # Email sending failed, but continue with OTP generation for development
        print("Warning: OTP email failed to send, but OTP was generated")

def validate_otp(request, user_otp):
    secret = request.session.get("otp_secret")
    return verify_otp(secret, user_otp)
