from .settings import *

DEBUG = True 

ALLOWED_HOSTS =['ec2-3-16-26-24.us-east-2.compute.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eventnet',
        'USER': 'eventnet_user',
        'PASSWORD': 'KMr$p*f543',
        'HOST': '127.0.0.1',
       # 'PORT': '5432',
    }
}

WEB_URL = "https://eventnet.ml/"
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
