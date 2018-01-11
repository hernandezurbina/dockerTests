--
-- Create user for myapp_schema
-- The password that goes in between quotes of IDENTIFIED BY statement should
-- match the password in $PROJECTDIR/myapp/myapp/settings_secret.py
--

GRANT ALL PRIVILEGES ON myapp_schema.* TO 'myapp_db_user'@'%' IDENTIFIED BY ''
