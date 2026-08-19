from pathlib import Path
import os

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, URL
from sqlalchemy.engine import Engine
import dotenv

PATH_DIR = Path(__file__).parent.resolve()
PATH_ENV = PATH_DIR / ".env"

if not PATH_ENV.exists():
    print(f".env file not found (looked at {PATH_ENV}). exiting...")
    exit(1)

dotenv.load_dotenv(PATH_ENV)

# registry of { TABLENAME: COLUMNS_TO_KEEP } to read from the input postgres db
KEEP_INPUT = {
    # full list: [ "id", "id_uuid", "id_richelieu", "iiif_url", "iiif_folio", "source_url", "date_source", "date_corr", "date", "technique", "description", "inscription", "corpus", "inventory_number", "produced", "represents", "id_licence" ],
    "iconography": [ "id", "id_uuid", "iiif_url", "source_url", "date", "technique", "corpus" ],
    # full list: [ "id", "id_uuid", "id_richelieu", "date", "centroid", "vector", "vector_source", "crs_epsg", "id_place_group ]
    "place": [ "id", "id_uuid", "date", "centroid", "vector" ],
    # full list: [  "id", "id_uuid", "address", "city", "country", "source", "date" ]
    "address": [  "id", "address", "source" ],
    # full list: [ "id", "id_uuid", "entry_name" ]
    "actor": [ "id", "id_uuid", "entry_name" ],
    # full list: [ "id", "id_uuid", "entry_name", "ismain", "id_iconography ]
    "title": [ "id", "entry_name", "ismain", "id_iconography" ],
    # full list: [ "id", "id_uuid", "entry_name", "description", "category", "category_slug" ]
    "theme": [ "id", "id_uuid", "entry_name", "description", "category", "category_slug" ],
    # full list:  [ "id", "id_uuid", "entry_name", "description" ]
    "institution": [ "id", "id_uuid", "entry_name"],
    # full list: [ "id", "id_uuid", "id_address", "id_place" ]
    "r_address_place": [ "id", "id_address", "id_place" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_place" ]
    "r_iconography_place": [ "id", "id_iconography", "id_place" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_theme" ] 
    "r_iconography_theme": [ "id", "id_iconography", "id_theme" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_actor", "role", "ismain" ]
    "r_iconography_actor": [ "id", "id_iconography", "id_actor", "role", "ismain" ],
    # full list: [ "id", "id_uuid", "id_cartography", "id_place" ]
    "r_cartography_place": [ "id", "id_cartography", "id_place" ],
}

def db_uri(params:dict) -> str:
    """
    create an URI to connect to the database based on the dict `params`
    """
    return sq.URL.create(
        "postgresql", 
        username=params['username'], 
        password=params["password"], 
        host=params["uri"],
        database=params["db"] 
    )

def make_pg_engine():
    env_vars = ["DB_NAME", "PG_HOST", "PG_PORT", "PG_USER", "PG_PASSWORD"]
    expected = [ k for k in env_vars if k != "PG_PASSWORD" ]  # PG_PASSWORD depends on how your pg_hba conf is set.
    credentials = { k: os.environ.get(k) for k in env_vars }
    assert all( credentials[k] for k in expected ), f"some .env variables are undefined. can't connect to postgres (env: {credentials})"

    url = URL.create(
        "postgresql", 
        username=credentials["PG_USER"], 
        password=credentials['PG_PASSWORD'], 
        host=credentials['PG_HOST'], 
        port=credentials['PG_PORT'],
        database=credentials["DB_NAME"]
    )

    return create_engine(url, echo=False)

class Database:
    """pandas dataframe representation of our postgres database"""
    def __init__(self, **kwargs):
        required = ["pg_engine"]
        for r in required:
            if not kwargs.get(r): 
                raise AttributeError(f"{r} is expected but missing !")
        self.pg_engine = kwargs.get("pg_engine")
        self._populate()
    
    # populate from a live postgres instance
    def _populate(self):
        for tablename, cols in KEEP_INPUT.items():
            # read table into df and only keep relevant columns
            df = (
                pd.read_sql(f"SELECT * FROM {tablename}", con=self.pg_engine, index_col=None)
                [cols]
            )
            # add each table to `self` so it can be accessed with self.df_{tablename}  
            setattr(self, f"df_{tablename}", df)
        return 

    def _assert_join_ok(self, df_left, df_right, left_col, right_col):
        """
        verify that a foreign-key relationship between two dataframes is valid,
        i.e. every non-null value in df_left[left_col] has a matching value
        in df_right[right_col].

        NOTE: order of `df_left`, `df_right` is important ! specify the tables such that: df_left[left_col] is a FK to df_right[right_col]
        NOTE: use before setting a default for NaN values !
        """
        left_ids = set(df_left[left_col].dropna())
        right_ids = set(df_right[right_col].dropna())
        unmatched = left_ids - right_ids

        assert not unmatched, (
            f"Join failed between {left_col!r} and {right_col!r}: "
            f"{len(unmatched)} value(s) in {left_col!r} have no match in {right_col!r}. "
            f"Examples: {list(unmatched)[:5]}"
        )

    def pipeline(self):
        # move title from its own foreign table to df_iconography.title => df_title becomes useless
        s_titles = self.df_title[self.df_title.ismain == True].set_index("id_iconography")["entry_name"]
        self.df_iconography["title"] = self.df_iconography["id"].map(s_titles)
        self._assert_join_ok(self.df_title, self.df_iconography, "id_iconography", "id")
        self.df_iconography.loc[self.df_iconography.title.isna()].title = "Sans titre"

        # move address name from its own table to df_place => df_address becomes useless. 
        df_address = self.df_address.loc[self.df_address.source=="contemporain"]
        df_r_address_place = self.df_r_address_place.loc[self.df_r_address_place.id_address.isin(df_address.id)] 
        df_address = self.df_address.set_index("id")["address"]
        print(df_address)
        df_r_address_place["address"] = df_r_address_place["id_address"].map(df_address)
        print(df_r_address_place[["id_address", "address"]])
        # df_r_address_place.address = self.df_address.loc[r_address_place.id_address

if __name__ == "__main__":
    engine = make_pg_engine()
    Database(pg_engine=engine).pipeline()