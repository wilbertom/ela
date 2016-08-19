-- Postgres ELA tables:

-- createdb -O pgela eladb_aug18 (as 'postgres' user)


CREATE TABLE user_type (
        id serial PRIMARY KEY,
        type character varying(45) NOT NULL
);

CREATE TABLE ela_users (
	id serial PRIMARY KEY,
	name character varying(45) NOT NULL,
        type integer NOT NULL,
        CONSTRAINT user_type_fkey FOREIGN KEY (type) REFERENCES user_type(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE materials (
        id serial PRIMARY KEY,
        name character varying(45) NOT NULL
);

CREATE TABLE proj_status (
        id serial PRIMARY KEY,
        name character varying(45) NOT NULL
);

CREATE TABLE projects (
	id serial PRIMARY KEY,
	name character varying(45) NOT NULL,
        status integer NOT NULL,
        CONSTRAINT status_id_fkey FOREIGN KEY (status) REFERENCES proj_status(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE users_projects (
        id serial PRIMARY KEY,
        user_id integer NOT NULL,
        project_id integer NOT NULL,
        CONSTRAINT user_id_fkey FOREIGN KEY (id) REFERENCES ela_users(id) ON UPDATE CASCADE ON DELETE RESTRICT,
        CONSTRAINT project_id_fkey FOREIGN KEY (id) REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE samples (
	id serial PRIMARY KEY,
	name character varying(100) NOT NULL,
	nickname character varying(45),
        material integer NOT NULL,
        CONSTRAINT material_id_fkey FOREIGN KEY (material) REFERENCES materials(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE device_type (
        id serial PRIMARY KEY,
        type character varying(45) NOT NULL
);

CREATE TABLE device_location (
        id serial PRIMARY KEY,
        location character varying(45) NOT NULL
);

CREATE TABLE devices (
	id serial PRIMARY KEY,
	name character varying(45) NOT NULL,
	type integer NOT NULL,
        location integer NOT NULL,
        CONSTRAINT device_type_fkey FOREIGN KEY (type) REFERENCES device_type(id) ON UPDATE CASCADE ON DELETE RESTRICT,
        CONSTRAINT device_location_fkey FOREIGN KEY (location) REFERENCES device_location(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE experiments (
	id serial PRIMARY KEY,
	device_id integer NOT NULL,
        ela_user_id integer NOT NULL,
	project_id integer NOT NULL,
        sample_id integer NOT NULL,
	date_created timestamp without time zone DEFAULT now(),
	CONSTRAINT device_id_fkey FOREIGN KEY (device_id) REFERENCES devices(id) ON UPDATE CASCADE ON DELETE RESTRICT,
        CONSTRAINT ela_user_id_fkey FOREIGN KEY (ela_user_id) REFERENCES ela_users(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	CONSTRAINT project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON UPDATE CASCADE ON DELETE RESTRICT,
        CONSTRAINT sample_id_fkey FOREIGN KEY (sample_id) REFERENCES samples(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE files (
        id serial PRIMARY KEY,
        experiment_id integer NOT NULL, 
        file_name character varying(250) NOT NULL,
        FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);
