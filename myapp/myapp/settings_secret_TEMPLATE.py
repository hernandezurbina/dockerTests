# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '' //your Django secret key should go here!

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myapp_schema',
        'USER': 'myapp_db_user',
        'PASSWORD': '', //your password to access the DB should be here and should match the password in $PROJECTDIR/db/db-dump/dbuser.sql
        'HOST': 'db',
        'PORT': '3306',
    }
}
