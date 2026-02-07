# accounts/otp.py
import pyotp

def generate_otp_secret():
    """Generates a new random base32 secret for TOTP."""
    return pyotp.random_base32()

def generate_otp(secret):
    """Generates a TOTP code for the given secret."""
    return pyotp.TOTP(secret).now()

def verify_otp(secret, user_input):
    """
    Verifies a user-submitted OTP.
    A valid_window of 1 allows for a 30-second tolerance on either side,
    which is usually sufficient to account for clock drift.
    """
    return pyotp.TOTP(secret).verify(user_input, valid_window=1)
