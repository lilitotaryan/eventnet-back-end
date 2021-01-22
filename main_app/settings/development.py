from .settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transaction_db',
        'USER': 'izabella',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = True
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_VERIFICATION_TEMPLATE = 'authentication/email_content.html'

WEB_URL = "http://127.0.0.1:8000/"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "eventnet1999@gmail.com"
EMAIL_HOST_PASSWORD = "TR37o*mw86"
RESET_PASSWORD_TEMPLATE = 'authentication/forgot_password.html'
EMAIL_VERIFICATION_TEMPLATE = 'authentication/email_content.html'
TICKET_TEMPLATE = 'buy_ticket/ticket.html'
SUBSCRIBE_TEMPLATE = "subscribe/subscription_email.html"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

STRIPE_API_KEY = "sk_test_Kaonx7eVGEMICZr3cnFhnMnX00iuLecNl6"
CHARGE_PERCENTAGE = 0
FREE_EVENT_CHARGE = 100000

CLIENT_ID = "ac_HPspZHGB0X4gIDRNfi2N070BQeDmoNiA"