FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD mypass

# COPY db-dump/myapp_schema.sql /usr/sql/myapp_schema.sql

COPY db-dump/13032019.sql /docker-entrypoint-initdb.d/
COPY db-dump/dbuser.sql /docker-entrypoint-initdb.d/

EXPOSE 3306

CMD ["mysqld"]
# RUN /etc/init.d/mysql start && \
#     mysql -u root -p${MYSQL_ROOT_PASSWORD} < /usr/sql/myapp_schema.sql && \
#     mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "GRANT ALL PRIVILEGES ON myapp_schema.* TO 'myapp_db_user'@'localhost' IDENTIFIED BY 'myapppassword'"
