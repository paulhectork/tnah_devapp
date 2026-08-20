CREATE TABLE author (
	id BIGINT, 
	name TEXT
);
CREATE TABLE theme (
	id BIGINT, 
	name TEXT, 
	richelieu_url TEXT
);
CREATE TABLE place (
	id BIGINT, 
	address TEXT, 
	richelieu_url TEXT, 
	loc JSON, 
	vector JSON, 
	date_lower BIGINT, 
	date_upper BIGINT
);
CREATE TABLE iconography (
	id BIGINT, 
	title TEXT, 
	iiif_manifest_url TEXT, 
	iiif_image_url TEXT, 
	source_url TEXT, 
	richelieu_url TEXT, 
	id_author BIGINT, 
	date_lower FLOAT, 
	date_upper FLOAT
);
CREATE TABLE iconography_place (
	id BIGINT, 
	id_iconography BIGINT, 
	id_place BIGINT
);
CREATE TABLE iconography_theme (
	id BIGINT, 
	id_iconography BIGINT, 
	id_theme BIGINT
);
