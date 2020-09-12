-- How a tagging file is originated.  Used as column type on the tagging.file table
CREATE TYPE tagging_file_origin_enum AS ENUM ('mycroft', 'selene', 'manual');
