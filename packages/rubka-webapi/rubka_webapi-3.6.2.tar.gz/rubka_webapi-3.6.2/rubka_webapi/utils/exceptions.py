# rubka_webapi/utils/exceptions.py

class RubikaException(Exception):
    """
    استثنای پایه برای خطاهای مربوط به کتابخانه rubka_webapi.
    """
    pass

class AuthException(RubikaException):
    """
    استثنا برای خطاهای احراز هویت.
    """
    pass

class NetworkException(RubikaException):
    """
    استثنا برای خطاهای شبکه.
    """
    pass

class InvalidParameterException(RubikaException):
    """
    استثنا برای پارامترهای نامعتبر.
    """
    pass

