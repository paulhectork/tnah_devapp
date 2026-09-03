import os
import re
import json
import random
from pathlib import Path
from typing import Any, Literal

import dotenv
import pandas as pd
import numpy as np
from tqdm import tqdm
from sqlalchemy import create_engine, text, URL
from sqlalchemy.engine import Engine
from sqlalchemy import types as sa_types
from psycopg2._range import NumericRange

PATH_DIR = Path(__file__).parent.resolve()
PATH_ROOT = PATH_DIR.parent.resolve()  # tnah_devapp/ folder
PATH_ENV = PATH_DIR / ".env"
PATH_OUT = PATH_ROOT
PATH_DB = PATH_OUT / "richelieu.db"
PATH_DATA = PATH_ROOT / "data"
PATH_ICONOGRAPHY_SAMPLE = PATH_DATA / "iconography_sample.csv"

PATH_DB_SCHEMA = PATH_OUT / "richelieu_schema.sql"

# registry of { TABLENAME: COLUMNS_TO_KEEP } to read from the input postgres db
# NOTE: tables not mentionned here are dropped
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
    # full list:  [   "id", "id_uuid", "id_iconography",  "id_cartography", "id_directory", "id_institution" ]
    "r_institution": [ "id", "id_uuid", "id_iconography", "id_institution" ],
    # full list: [ "id", "id_uuid", "id_address", "id_place" ]
    "r_address_place": [ "id", "id_address", "id_place" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_place" ]
    "r_iconography_place": [ "id", "id_iconography", "id_place" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_theme" ] 
    "r_iconography_theme": [ "id", "id_iconography", "id_theme" ],
    # full list: [ "id", "id_uuid", "id_iconography", "id_actor", "role", "ismain" ]
    "r_iconography_actor": [ "id", "id_iconography", "id_actor", "role", "ismain" ],
    # # full list: [ "id", "id_uuid", "id_cartography", "id_place" ]
    # "r_cartography_place": [ "id", "id_cartography", "id_place" ],
}


def make_engine(flavor: Literal["sqlite", "postgresql"]) -> Engine:
    env_vars = ["DB_NAME", "PG_HOST", "PG_PORT", "PG_USER", "PG_PASSWORD"]
    if flavor == "postgresql":
        expected = [ k for k in env_vars if k != "PG_PASSWORD" ]  # PG_PASSWORD depends on how your pg_hba conf is set.
    else:
        expected = [ "DB_NAME" ]
    credentials = { k: os.environ.get(k) for k in env_vars }
    assert all( credentials[k] for k in expected ), f"some .env variables are undefined. can't connect to postgres (env: {credentials})"

    if flavor == "postgresql": 
        url = URL.create(
            "postgresql", 
            username=credentials["PG_USER"], 
            password=credentials['PG_PASSWORD'], 
            host=credentials['PG_HOST'], 
            port=credentials['PG_PORT'],
            database=credentials["DB_NAME"]
        )
    else:
        url = f"sqlite:///{PATH_DB}"
    return create_engine(url, echo=False)


# create the structure of the output database from an SQLite schema definition
def create_output_database(engine: Engine):
    with open(PATH_DB_SCHEMA, mode="r") as f:
        sql_schema = f.read()
    # sqlite can only execute 1 statement at a time
    sql_statements = sql_schema.split(";")
    with engine.begin() as conn:
        for statement in sql_statements:
            conn.execute(text(statement))
    print(f"created database from schema: '{PATH_DB_SCHEMA}'")
    return 


class MigrationPipeline:
    """migration pipeline: from the full Richelieu postgres database to a smaller sqlalchemy database"""
    def __init__(self, **kwargs):
        required = ["pg_engine", "sqlite_engine"]
        for r in required:
            if not kwargs.get(r): 
                raise AttributeError(f"{r} is expected but missing !")

        # create database
        self.pg_engine = kwargs.get("pg_engine")
        self.sqlite_engine = kwargs.get("sqlite_engine")
        return

    # return a generator of (df_name, df) for each dataframe defined in `self` 
    def _iter_dfs(self):
        # df_name -> df
        df_dict = { 
            k: v 
            for k, v in self.__dict__.items()
            if isinstance(v, pd.DataFrame)
        }
        for df_name, df in df_dict.items():
            yield (df_name, df)

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
            f"duplicate values in df_right[{right_col!r}]: {list(dupes)[:5]} (total={len(dupes)}). "
            f"a left join against this would produce unreliable results."
        )

        # 2. existence check
        left_ids = set(df_left[left_col].dropna())
        right_ids = set(df_right[right_col].dropna())
        unmatched = left_ids - right_ids
        assert not unmatched, (
            f"join failed between {left_col!r} and {right_col!r}: "
            f"{len(unmatched)} value(s) in {left_col!r} have no match in {right_col!r}. "
            f"examples: {list(unmatched)[:5]}"
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
                    f"merge produced incorrect values in column {col!r} for "
                    f"{mismatch.sum()} row(s). example bad rows (index): "
                    f"{df_left.index[mismatch].tolist()[:5]}"
                )

    # read tables from a live pg instance to dataframes
    def _populate(self):
        for tablename, cols in KEEP_INPUT.items():
            # read table into df and only keep relevant columns
            df = (
                pd.read_sql(f"SELECT * FROM {tablename}", con=self.pg_engine, index_col=None)
                [cols]
            )
            # add each table to `self` so it can be accessed with self.df_{tablename}  
            setattr(self, f"df_{tablename}", df)
        return self

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
        bnf = "Bibliothèque nationale de France"
        id_bnf = self.df_institution.loc[self.df_institution.entry_name.eq(bnf)].id.squeeze()
        # iconography IDs to keep
        s_iconography = self.df_r_institution.loc[
            self.df_r_institution.id_institution.eq(id_bnf)
            & ~self.df_r_institution.id_iconography.isna()
        ]["id_iconography"]
        mask = self.df_iconography.id.isin(s_iconography)
        self.df_iconography.loc[mask, "institution"] = "Bibliothèque nationale de France"
        # NOTE: those rows are deleted in `_filter_rows`
        self.df_iconography.loc[~mask, "institution"] = None
        icono_bnf_count = self.df_iconography.loc[self.df_iconography.institution.eq(bnf)].shape[0]
        assert icono_bnf_count == s_iconography.shape[0], f"expected {s_iconography.shape[0]} iconography ressources for institution '{bnf}', got {icono_bnf_count}"
        
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

    # for each ressource where it's possible, add an URL to the Quartier Richelieu website page. 
    def _add_urls(self):
        mapper = {
            "df_theme": lambda x: f"https://quartier-richelieu.inha.fr/theme/{x}",
            "df_iconography": lambda x: f"https://quartier-richelieu.inha.fr/iconographie/{x}",
            "df_place": lambda x: f"https://quartier-richelieu.inha.fr/lieu/{x}",
        }
        for df_name, f in mapper.items():
            df = getattr(self, df_name)
            df["richelieu_url"] = df["id_uuid"].apply(f)
            setattr(self, df_name, df)
        return self
    
    # NOTE: instead of fetching the manifests to retrieve an image, we just do a regex-based reconstruction of the image URL.
    # gallica is just too annoying to request and i've been blocked nonstop from it.
    def _get_iiif_images(self):
        self.df_iconography["iiif_image_url"] = None
        mask = ~self.df_iconography.iiif_url.isna()
        self.df_iconography.loc[mask, "iiif_image_url"] = (
            self.df_iconography
            .loc[mask, "iiif_url"]
            .str.replace("/manifest.json", "/f1/full/1000/0/native.jpg")
        )
        return self

    def _filter_rows(self):
        """
        - drop rows violating null constraints on our db
        - keep only rows where iconography.institution == "Bibliothèque nationale de France"
        - cascade the above: drop rows from other tables that have no relationship to iconography
        """
        # REGISTER OF PROCESSED TABLES TO AVOID INFINITE RECURSION
        processed = []
        def drop_cascade(df: pd.DataFrame, df_name: str, colname: str, keep_vals: pd.Series) -> pd.DataFrame:
            """
            `colname` is a foreign key column.
            delete rows from `df` where `df[colname]` is not in `keep_vals`. 
            if `df` contains a foreign key to another table, propagate deletion: 
            select this foreign table (`df_foreign`) and recursively delete rows 
            where `df_foreign[id]` is not in `df.id`. repeat with foreign keys in 
            `df_foreign` until all cascades have been completed.
            (i.e.: delete rows from df_r_iconography_theme without a reference to df_iconography. 
            then, delete rows in df_theme not referenced to df_r_iconography_theme)
            (foreign key column is named `{foreign_df_name.replace("^df_", "id_")}`, 
            hence how we can target the foreign tables from foreign keys directly)
            """
            if colname in df.columns:
                # size_pre = df.shape[0]
                df = df.loc[df[colname].isin(keep_vals)]
                # size_post = df.shape[0]
                # print(f"* (curr) working on: {df_name}[{colname}]")
                # print(f"* (curr) dropped {100*(size_pre-size_post)/size_pre}% rows ({size_pre-size_post} dropped, # post rows: {size_post})")
                fk_cols = [col for col in df.columns if col.startswith("id_") and col != "id_uuid"]
                setattr(self, df_name, df)
                # avoid infinite recursion by keeping a register of processed tables 
                processed.append(df_name)
                for fk_col in fk_cols:
                    foreign_df_name = re.sub(r"^id_", "df_", fk_col)
                    if foreign_df_name in processed:
                        continue
                    foreign_keep_vals = df[fk_col]
                    foreign_colname = "id"
                    foreign_df = getattr(self, foreign_df_name)
                    # print("* (next) foreign_df_name:", foreign_df_name)
                    # print("* (next) foreign_colname:", foreign_colname)
                    # print("*"*10)
                    drop_cascade(foreign_df, foreign_df_name, foreign_colname, foreign_keep_vals)
            return

        self.df_iconography = self.df_iconography.loc[
            ~self.df_iconography.iiif_url.isna()
            & self.df_iconography.institution.eq("Bibliothèque nationale de France")
        ]
        # propagate above deletion of rows in self.df_iconography 
        s_iconography_ids = self.df_iconography.id
        for df_name, df in self._iter_dfs():
            if df_name == "df_iconography":
                continue
            if "id_iconography" in df.columns:
                drop_cascade(df, df_name, "id_iconography", s_iconography_ids)
        return self

    def _reset_ids(self):
        """
        in `_filter_rows` we slice each table to keep only rows that will end up referencing
        iconography rows where institution = bnf
        => table ids are now discontinuous => reset all id cols in all tables by 1..n 
        and propagate to foreign key cols 
        """
        # count number of nan values in a series to check that no data loss happened in a resetting
        isna_count = lambda s: s[s.notnull()].shape[0]

        for df_name, df in self._iter_dfs():
            fk_name = re.sub("^df_", "id_", df_name)
            df["id_og"] = df.id
            # replace the old ID with a new one (int, autoincremented) 
            df.id = np.arange(1, df.shape[0] + 1)
            # make a mapper of (old_id, new_id) to update foreign keys to `df` in other columns. 
            # for the map to work in pandas the name of the mapper series MUST be the same as the 
            # name of the column whose values we want to update => mapper series must be named `fk_name`, 
            # because the fk to `df` in other tables is also named `fk_name`. 
            s_mapper = (
                df[["id", "id_og"]]
                .set_index("id_og")
                .rename(columns={"id": fk_name})
                [fk_name]
            )
            # drop the "id_og" column
            df = df[[ col for col in df.columns if col != "id_og" ]]
            setattr(self, df_name, df)
            # update foreign keys to `df` in other tables
            for foreign_df_name, foreign_df in self._iter_dfs():
                if df_name != foreign_df_name and fk_name in foreign_df.columns:
                    isna_pre = isna_count(foreign_df[fk_name])
                    foreign_df[fk_name] = foreign_df[fk_name].map(s_mapper)
                    isna_post = isna_count(foreign_df[fk_name])
                    assert isna_pre == isna_post, f"foreign keys lost in: _reset_ids. col: {foreign_df_name}[{fk_name}], pre={isna_pre}, post={isna_post}, change={isna_pre-isna_post}"
                    setattr(self, foreign_df_name, foreign_df)
        return self

    # drop useless fields from each table + rename fields
    def _drop_and_rename_fields(self):
        for df_name, df in self._iter_dfs():
            # drop id_uuid fields
            df = df[[ c for c in df.columns if c != "id_uuid" ]]
            setattr(self, df_name, df)

        # tablename -> [ [fields to keep], {fields to rename} ]
        mapper = {
            "df_iconography": [
                ['id', 'title', 'date', 'iiif_url', 'iiif_image_url', 'source_url', 'richelieu_url', 'institution', 'id_author'],
                {"iiif_url": "iiif_manifest_url"}
            ],
            "df_author": [
                ['id', 'entry_name'],
                { "entry_name": "author_name" }
            ],
            "df_place": [
                ['id', 'address', 'date', 'richelieu_url', 'centroid', 'vector'],
                { "centroid": "loc", "vector": "plot" }
            ],
            "df_theme": [
                ['id', 'entry_name', 'richelieu_url'],
                { "entry_name": "theme_name" }
            ],
        }
        for df_name, [cols, rename_mapper] in mapper.items():
            df = getattr(self, df_name)
            df = df[cols]
            df = df.rename(columns=rename_mapper)
            setattr(self, df_name, df)
        return self

    # cast columns to specific types
    def _cast_types(self):
        def numericrange_to_inttuple(x: NumericRange|Any) -> tuple[int|float]:
            return (x.lower, x.upper) if isinstance(x, NumericRange) else (np.nan, np.nan)

        # transform `date` in `date_lower` and `date_upper` columns
        for df_name, df in self._iter_dfs():
            if "date" in df.columns:
                df["date"] = df["date"].apply(numericrange_to_inttuple)
                df["date_lower"] = df["date"].apply(lambda x: x[0])
                df["date_upper"] = df["date"].apply(lambda x: x[1])
                df = df.drop(columns="date")
            setattr(self, df_name, df)

        # nullable FKs should contain mixed types: int+None. in Pandas, that's impossible 
        # and ints are converted to float, none to np.nan. 
        # => cast to pd.Int64Dtype, which allows both int and nan values
        for df_name, df in self._iter_dfs():
            cols = [c for c in df.columns if c.startswith("id") or c.startswith("date")]
            df[cols] = df[cols].astype(pd.Int64Dtype())
            setattr(self, df_name, df)
        return self

    # remove `n_rows` rows from the output `Iconography` and save them to a CSV file. 
    # this sample data can be added by hand in the app during classes  
    def _sample_manual(self):
        n_rows = 20
        df_iconography = self.df_iconography.copy()
        df_sample = self.df_iconography[:n_rows]
        df_iconography = self.df_iconography[n_rows:]
        df_sample.to_csv(PATH_ICONOGRAPHY_SAMPLE, index=False)
        print(f"wrote {n_rows} sample iconography rows to '{PATH_ICONOGRAPHY_SAMPLE}'")
        self.df_iconography = df_iconography
        return self

    def _to_sql(self):
        # NOTE: order is important
        tables = [
            "author",
            "theme",
            "place",
            "iconography",
            "r_iconography_place",
            "r_iconography_theme",
        ]
        # tablename -> { colname: sql type }
        type_mapper = { "place": {"loc": sa_types.JSON, "plot": sa_types.JSON}  }
        
        nrows_total = 0

        print("beginning table creation...")

        # insert !
        params = { "if_exists": "append", "index": False }
        with self.sqlite_engine.begin() as conn:
            for table in tables:
                df = getattr(self, f"df_{table}")

                nrows = df.shape[0]
                nrows_total += nrows
                print(f"* inserting {table} ({nrows} rows)")

                params = { "con": conn, **params }
                if table in type_mapper: 
                    params["dtype"] = type_mapper[table]
                else:
                    # let sqlite handle type coercion
                    params["dtype"] = False

                # remove leading `r_` from relation tablenames
                table = re.sub(r"^r_", "", table)
                df.to_sql(table, **params)

        print(f"database insertion pipeline finished ! {len(tables)} tables, {nrows_total} rows inserted")
        print(f"find the created database at: {PATH_DB}")
        return

    def pipeline(self):
        (
            self
            ._populate()
            ._joins()
            ._filter_rows()
            ._reset_ids()
            ._get_iiif_images()
            ._add_urls()
            ._drop_and_rename_fields()
            ._cast_types()
            ._sample_manual()
            ._to_sql()
        )
        

if __name__ == "__main__":
    # init stuff
    if not PATH_ENV.exists():
        print(f".env file not found (looked at {PATH_ENV}). exiting...")
        exit(1)

    PATH_OUT.mkdir(exist_ok=True)
    PATH_DATA.mkdir(exist_ok=True)
    if PATH_DB.is_file():
        PATH_DB.unlink()
    if not PATH_DB_SCHEMA.is_file():
        print(f"schema of the output database not found (looked at: '{PATH_DB_SCHEMA}') ! can't guarantee schema of created database. exiting...")
        exit(1)

    dotenv.load_dotenv(PATH_ENV)

    # create engines
    pg_engine = make_engine("postgresql")
    sqlite_engine = make_engine("sqlite")

    # create output database schema by executing SQL schema defined at root of tnah_devapp
    create_output_database(sqlite_engine)

    # make migration and create new db
    MigrationPipeline(pg_engine=pg_engine, sqlite_engine=sqlite_engine).pipeline()


# NOTE: backup of async stuff in MigrationPipeline
#   Gallica is unfortunately too difficult to work with .,
# 
# import asyncio
# import tenacity
# from tqdm.asyncio import tqdm_asyncio
# 
#     # NOTE: in __init__
#         # async stuff
#         # _session is defined in `__aenter__` / closed in `__aexit__`
#         self.max_connections = 1 # NIK GALLICA et ses blocages expresssssssss
#         self._session: aiohttp.ClientSession | None = None
#         self.semaphore = asyncio.Semaphore(self.max_connections)
#         return
# 
#     # NOTE: defining __aenter__ / __aexit__ turns this clas into an async content manager
#     async def __aenter__(self) -> "SasExporterBase":
#         self._session = aiohttp.ClientSession(
#             # NOTE TCPConnector limit must be higher than Semaphore limit
#             # so that the aiohttp.Session queue is always empty
#             # (otherwise, risk of timeouts, stale connections etc.)
#             connector=aiohttp.TCPConnector(limit=self.max_connections+5),
#             # NOTE: useful to avoid getting blocked by the server
#             headers = {
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
# 
#             },
#             timeout=aiohttp.ClientTimeout(
#                 total=None,        # no hard cap on the full lifecycle
#                 connect=None,      # no cap on pool wait + sock_connect combined
#                 sock_connect=10,   # timeout for TCP handshake/DNS only, excludes pool wait
#                 sock_read=30       # timeout waiting for server response after request is sent
#             )
#         )
#         return self
# 
#     async def __aexit__(self, *args) -> None:
#         if self._session:
#             await self._session.close()
#             self._session = None
# 
#     @property
#     def session(self) -> aiohttp.ClientSession:
#         if self._session is None:
#             raise RuntimeError(f"{self.__class__} must be used as an async context manager")
#         return self._session
#     
#     # asynchronous fetch
#     # retry 5 times, waiting 1-5 seconds between each
#     @tenacity.retry(
#         retry=tenacity.retry_if_exception_type(aiohttp.ClientResponseError),
#         stop=tenacity.stop_after_attempt(5),
#         wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
#         reraise=True  # if it still fails, raise the original error instead of tenacity.RetryError.
#     )
#     async def _fetch_to_json(self, url: str) -> dict:
#         async with self.semaphore:
#             async with self.session.get(url) as response:
#                 response.raise_for_status()
#                 r_text = await response.text()
#         return json.parse(r_text)
# 
#     async def _get_iiif_images(self):
#         errors = []
#         async def inner(iiif_url: str) -> str:
#             try:
#                 manifest = await self._fetch_to_json(url=iiif_url)
#                 id_img = id_img.replace("/full/full/", "/full/1000/")  # clip size to 1000px
#                 return id_img
#             except Exception as e:
#                 errors.append(iiif_url)
#                 print(f"failed to fetch {iiif_url}: {e!r}")
#                 return None
#         df = self.df_iconography[["id", "iiif_url"]].loc[~self.df_iconography.iiif_url.isna()].copy()
#         df["iiif_image_url"] = await tqdm_asyncio.gather(
#             *[ inner(iiif_url) for iiif_url in df.iiif_url ],
#             desc="fetching IIIF image URLs"
#         )
#         # TODO complete self.df_iconography with df.iiif_image_url
# 
#     async def pipeline_async(self):
#         async with self:        
#             (
#                 self
#                 ._populate()
#                 ._joins()
#             )
#             await self._get_iiif_images()
#             (
#                 self
#                 ._add_urls()
#                 ._drop_and_rename_fields()
#                 ._cast_types()
#                 ._to_sql()
#             )
#         return
# 
#     async def pipeline(self):
#         asyncio.run(self.pipeline_async())



