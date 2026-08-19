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
    "address": [ "id", "address", "source" ],
    # full list: [ "id", "id_uuid", "entry_name" ]
    "actor": [ "id", "id_uuid", "entry_name" ],
    # full list: [ "id", "id_uuid", "entry_name", "ismain", "id_iconography ]
    "title": [ "id", "entry_name", "ismain", "id_iconography" ],
    # full list: [ "id", "id_uuid", "entry_name", "description", "category", "category_slug" ]
    "theme": [ "id", "id_uuid", "entry_name", "description", "category", "category_slug" ],
    # full list:  [ "id", "id_uuid", "entry_name", "description" ]
    "institution": [ "id", "id_uuid", "entry_name"],
    # full list:  [   "id", "id_uuid", "id_iconography", "id_cartography", "id_directory", "id_institution" ]
    "r_institution": [ "id", "id_uuid", "id_iconography", "id_cartography", "id_directory", "id_institution" ],
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

    def _assert_join_ok(self, df_left, df_right, left_col, right_col, value_cols=None):
        """
        verify that a merge/join between two dataframes is valid:
        1. df_right[right_col] has no duplicate keys (required for a clean 1:1 lookup)
        2. every non-null value in df_left[left_col] has a matching value in df_right[right_col]
        3. (optional) for each column in value_cols, the values in df_left actually match
            what a direct lookup in df_right would produce — catches row misalignment,
            row duplication, or accidental overwrites, not just missing keys

        NOTE: order of df_left, df_right matters! df_left[left_col] should be a FK to df_right[right_col]
        NOTE: call this AFTER merging but BEFORE dropping left_col / setting NaN defaults,
              since the value_cols correctness check needs left_col still present in df_left
        """
        # 1. duplicate keys on the right side make joins ambiguous / cause row multiplication
        dupes = df_right[right_col][df_right[right_col].duplicated()].unique()
        assert len(dupes) == 0, (
            f"Duplicate values in df_right[{right_col!r}]: {list(dupes)[:5]} (total={len(dupes)}). "
            f"A left join against this would produce unreliable results."
        )

        # 2. existence check
        left_ids = set(df_left[left_col].dropna())
        right_ids = set(df_right[right_col].dropna())
        unmatched = left_ids - right_ids
        assert not unmatched, (
            f"Join failed between {left_col!r} and {right_col!r}: "
            f"{len(unmatched)} value(s) in {left_col!r} have no match in {right_col!r}. "
            f"Examples: {list(unmatched)[:5]}"
        )

        # 3. row-level correctness check (optional)
        if value_cols:
            if isinstance(value_cols, str):
                value_cols = [value_cols]
            lookup = df_right.set_index(right_col)
            for col in value_cols:
                expected = df_left[left_col].map(lookup[col])
                actual = df_left[col]
                mismatch = ~((expected == actual) | (expected.isna() & actual.isna()))
                assert not mismatch.any(), (
                    f"Merge produced incorrect values in column {col!r} for "
                    f"{mismatch.sum()} row(s). Example bad rows (index): "
                    f"{df_left.index[mismatch].tolist()[:5]}"
                )


    def _joins(self):
        """
        handle relationships between tables: to simplify the model, resolve joins:
        - iconography-institution stops being a many-to-one relationship:
            the BNF is the only institution kept, and so institution 
            and r_institution are deleted.
        - iconography-actor stops being a many-to-many relationship
            and is replaced by a many-to-one relationship between 
            iconography and authors (info on publishers is lost)
        - place-address stops being a many-to-many relationship: 
            the contemporary address is selected and moved to place
        - iconography-title stops being a one-to-many relationship:
            the main title is extracted and moved to iconography  

        at the end, we have the following tables/dfs:
        - iconography
        - place
        - autor
        - theme
        - r_iconography_place
        - r_iconography_theme

        and the other tables/dfs are deleted
        """
        # INSTITUTION
        # - keep only the inconography rows for institution=BNF
        # - delete r_institution and institution tables
        id_bnf = self.df_institution.loc[self.df_institution.entry_name.eq("Bibliothèque nationale de France")].id.squeeze()
        s_iconography = self.df_r_institution.loc[
            self.df_r_institution.id_institution.eq(id_bnf)
            & ~self.df_r_institution.id_iconography.isna()
        ]["id_iconography"]
        self.df_iconography = self.df_iconography.loc[self.df_iconography.id.isin(s_iconography)]
        assert self.df_iconography.shape[0] == s_iconography.shape[0], f"expected shape shapes after dropping other institutions"
        
        # TITLE
        # move title from its own foreign table to df_iconography.title => df_title becomes useless
        self.df_title = (
            self.df_title[self.df_title.ismain == True]
            [["id_iconography", "entry_name"]]
            .rename(columns={"entry_name": "title"})
        )
        self.df_iconography = self.df_iconography.merge(
            self.df_title, left_on="id", right_on="id_iconography", how="left"
        )
        self._assert_join_ok(
            self.df_iconography, self.df_title, "id_iconography", "id_iconography", value_cols="title"
        )
        self.df_iconography = self.df_iconography.drop(columns="id_iconography")
        self.df_iconography.loc[self.df_iconography.title.isna(), "title"] = "Sans titre"

        # ADDRESS
        # move address name from its own table to df_place => df_address becomes useless
        # 1. keep only 'contemporain' addresses
        self.df_address = self.df_address.loc[self.df_address.source == "contemporain"]
        self.df_r_address_place = self.df_r_address_place.loc[
            self.df_r_address_place.id_address.isin(self.df_address.id)
        ]
        # 2. move df_address.address to df_r_address_place.address
        self.df_r_address_place = self.df_r_address_place.merge(
            self.df_address[["id", "address"]], left_on="id_address", right_on="id",
            how="left", suffixes=("", "_merge")
        ).drop(columns="id_merge")
        self._assert_join_ok(
            self.df_r_address_place, self.df_address, "id_address", "id", value_cols="address"
        )
        # 3. move df_r_address_place.[id_address, address] to df_place
        self.df_place = self.df_place.merge(
            self.df_r_address_place[["id_place", "address"]],
            left_on="id", right_on="id_place", how="left"
        )
        self._assert_join_ok(
            self.df_place, self.df_r_address_place, "id_place", "id_place",
            value_cols=["address"]
        )
        self.df_place = self.df_place.drop(columns="id_place")

        # ACTORS:
        # iconography-to-actor relationship:
        # - drop info on the editors
        # - select only the `main` author (r_iconography_actor.ismain = True)
        # - replace the many-to-many relationship to a many to one (1 actor row => many iconography rows)  
        self.df_r_iconography_actor = self.df_r_iconography_actor.loc[
            self.df_r_iconography_actor["ismain"].eq(True)
            & self.df_r_iconography_actor["role"].eq("author")
        ]
        self.df_iconography = (
            self.df_iconography.merge(
                self.df_r_iconography_actor[["id_iconography", "id_actor"]], 
                left_on="id", right_on="id_iconography", how="left"
            )
            .drop(columns="id_iconography")
            .rename(columns={"id_actor": "id_author"})
        )
        self.df_author = self.df_actor[ self.df_actor.id.isin(self.df_r_iconography_actor["id_actor"].unique()) ]
        assert self.df_iconography.loc[
            ~self.df_iconography.id_author.isna() 
            & ~self.df_iconography.id_author.isin(self.df_author.id)
        ].shape[0] == 0, "Undefined references from df_iconography to df_author"
        
        del self.df_institution
        del self.df_title
        del self.df_address
        del self.df_r_institution
        del self.df_r_address_place
        del self.df_r_iconography_actor
        del self.df_actor

        return self

    def _add_urls(self):
        """
        for each ressource where it's possible, add an URL to the Quartier Richelieu website page. 
        """
        mapper = {
            "theme": lambda x: f"https://quartier-richelieu.inha.fr/theme/{x}",
            "iconography": lambda x: f"https://quartier-richelieu.inha.fr/iconographie/{x}",
            "place": lambda x: f"https://quartier-richelieu.inha.fr/lieu/{x}",
        }
        for t, f in mapper.items():
            df_name = f"df_{t}"
            df = getattr(self, df_name)
            df["url_richelieu"] = df["id_uuid"].apply(f)
            setattr(self, df_name, df)
        return self

    def pipeline(self):
        (
            self
            ._joins()
            ._add_urls()
            ._drop_fields()
        )
        print(self.df_iconography.columns)

if __name__ == "__main__":
    engine = make_pg_engine()
    Database(pg_engine=engine).pipeline()