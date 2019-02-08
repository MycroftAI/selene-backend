-- create the roles that will be used by selene applications
CREATE ROLE selene WITH NOLOGIN;
CREATE ROLE selene_crud WITH LOGIN ENCRYPTED PASSWORD 'crud' IN GROUP selene;
CREATE ROLE selene_view WITH LOGIN ENCRYPTED PASSWORD 'view' IN GROUP selene;