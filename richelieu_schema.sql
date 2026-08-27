CREATE TABLE author (
	id INTEGER PRIMARY KEY, 
	author_name TEXT NOT NULL UNIQUE
);
CREATE TABLE theme (
	id INTEGER PRIMARY KEY, 
	theme_name TEXT NOT NULL UNIQUE, 
	richelieu_url TEXT NOT NULL UNIQUE
);
CREATE TABLE place (
	id INTEGER PRIMARY KEY, 
	address TEXT, 
	richelieu_url TEXT NOT NULL UNIQUE, 
	loc JSON  NOT NULL, 
	plot JSON  NOT NULL, 
	date_lower INTEGER, 
	date_upper INTEGER
);
CREATE TABLE iconography (
	id INTEGER PRIMARY KEY, 
	title TEXT NOT NULL, 
	iiif_manifest_url TEXT NOT NULL, 
	iiif_image_url TEXT NOT NULL, 
	source_url TEXT, 
	richelieu_url TEXT NOT NULL UNIQUE, 
	date_lower INTEGER, 
	date_upper INTEGER,
	institution TEXT NOT NULL,
	id_author INTEGER,
	FOREIGN KEY (id_author) REFERENCES author(id)
);
CREATE TABLE user (
	id INTEGER PRIMARY KEY,
	user_name TEXT NOT NULL,
	user_mail TEXT NOT NULL
);
CREATE TABLE iconography_place (
	id INTEGER PRIMARY KEY, 
	id_iconography INTEGER NOT NULL, 
	id_place INTEGER NOT NULL,
	FOREIGN KEY (id_iconography) REFERENCES iconography(id),
	FOREIGN KEY (id_place) REFERENCES place(id)
);
CREATE TABLE iconography_theme (
	id INTEGER PRIMARY KEY, 
	id_iconography INTEGER NOT NULL, 
	id_theme INTEGER NOT NULL,
	FOREIGN KEY (id_iconography) REFERENCES iconography(id),
	FOREIGN KEY (id_theme) REFERENCES theme(id)
);
CREATE TABLE iconography_user (
	id INTEGER PRIMARY KEY, 
	id_iconography INTEGER NOT NULL, 
	id_user INTEGER NOT NULL,
	FOREIGN KEY (id_iconography) REFERENCES iconography(id),
	FOREIGN KEY (id_user) REFERENCES user(id)
);