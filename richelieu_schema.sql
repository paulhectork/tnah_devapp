CREATE TABLE author (
	id INTEGER PRIMARY KEY UNIQUE, 
	author_name TEXT NOT NULL UNIQUE
);
CREATE TABLE theme (
	id INTEGER PRIMARY KEY UNIQUE, 
	theme_name TEXT NOT NULL UNIQUE, 
	richelieu_url TEXT NOT NULL UNIQUE
);
CREATE TABLE place (
	id INTEGER PRIMARY KEY UNIQUE, 
	address TEXT, 
	richelieu_url NOT NULL UNIQUE, 
	loc JSON  NOT NULL, 
	plot JSON  NOT NULL, 
	date_lower INTEGER, 
	date_upper INTEGER
);
CREATE TABLE iconography (
	id INTEGER PRIMARY KEY UNIQUE, 
	title TEXT NOT NULL, 
	iiif_manifest_url TEXT NOT NULL, 
	iiif_image_url TEXT NOT NULL, 
	source_url TEXT, 
	richelieu_url TEXT NOT NULL UNIQUE, 
	date_lower FLOAT, 
	date_upper FLOAT,
	id_author INTEGER,
	FOREIGN KEY (id_author) REFERENCES author(id)
);
CREATE TABLE iconography_place (
	id INTEGER PRIMARY KEY UNIQUE, 
	id_iconography INTEGER NOT NULL, 
	id_place INTEGER NOT NULL,
	FOREIGN KEY (id_iconography) REFERENCES iconography(id),
	FOREIGN KEY (id_place) REFERENCES place(id)
);
CREATE TABLE iconography_theme (
	id INTEGER PRIMARY KEY UNIQUE, 
	id_iconography INTEGER NOT NULL, 
	id_theme INTEGER NOT NULL,
	FOREIGN KEY (id_iconography) REFERENCES iconography(id),
	FOREIGN KEY (id_theme) REFERENCES theme(id)
);
