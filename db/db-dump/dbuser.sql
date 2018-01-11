--
-- Create user for myapp_schema
--

GRANT ALL PRIVILEGES ON myapp_schema.* TO 'myapp_db_user'@'%' IDENTIFIED BY 'mypass'
