GRANT USAGE ON SCHEMA account TO selene_crud;
GRANT USAGE ON SCHEMA account to selene_view;
GRANT SELECT ON ALL TABLES IN SCHEMA account TO selene_crud, selene_view;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA account TO selene_crud;
