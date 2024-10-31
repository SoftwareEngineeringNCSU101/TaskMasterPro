# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['*']

# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'patilharshvardhan0508@gmail.com'  # Your email address
EMAIL_HOST_PASSWORD = 'axhw zdeb arbn tffc'  # Your Gmail password or App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
