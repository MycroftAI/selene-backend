-- create the roles that will be used by selene applications
CREATE ROLE mycroft SUPERUSER LOGIN ENCRYPTED PASSWORD 'holmes';
CREATE ROLE appuser WITH NOLOGIN;
CREATE ROLE selene WITH LOGIN ENCRYPTED PASSWORD 'adam' IN GROUP appuser;
