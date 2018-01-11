# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8+&tu-oz3cwz%+r0k(cbylix4mxfx7q)_#d!i=057awm@nxja_'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myapp_schema',
        'USER': 'myapp_db_user',
        'PASSWORD': 'mypass',
        'HOST': 'db',
        'PORT': '3306',
    }
}
