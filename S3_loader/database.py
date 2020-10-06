import sqlite3

from S3_loader.checker import parse_period, parse_point


class Database:
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        self.c = self.conn.cursor()

    def table_exists(self, table_name):
        q = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        return len(self.c.execute(q).fetchall()) != 0

    def create_products_table(self, product_type):
        with self.conn:
            self.c.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {product_type}
                (
                prod_id INTEGER PRIMARY KEY,
                point_id INTEGER REFERENCES points (point_id),
                uuid TEXT,
                name TEXT,
                datetime TEXT,
                size TEXT,
                loaded INT,
                offline INT,
                in_daac INT,
                CONSTRAINT unq UNIQUE(uuid, point_id)
                ) 
                """
            )

    def insert_results(self, results, product_type):
        with self.conn:
            self.c.executemany(
                f"""
                INSERT OR IGNORE INTO {product_type}
                (uuid, name, datetime, size, point_id) 
                VALUES (?, ?, ?, ?, ?)
                """,
                zip(results['uuids'], results['names'], results['dates'], results['sizes'], results['point_id'])
            )

    def select_uuids_names(self, product_type, period=None):
        q = f"SELECT uuid, name FROM {product_type}"
        if period is not None:
            date_start, date_end = parse_period(period)
            q += f" WHERE datetime BETWEEN '{date_start}' AND '{date_end}'"
        self.c.execute(q)
        return self.c.fetchall()

    # def set_loaded(self, load_path, product_type):
    #     # ids = [self.get_prod_id_from_name(x[:-5], instrument) for x in os.listdir(load_path)]  # cut .SEN3 == os.path.splittext()[0]
    #     with self.conn:
    #         self.c.execute(
    #             f"""
    #             UPDATE products_{product_type}
    #             SET loaded = 1
    #             WHERE prod_id in {tuple(ids + [0])}  -- to remove a warning if tuple has one element (id,)
    #             """
    #         )
    #
    # def set_offline(self, uuids, product_type):
    #     with self.conn:
    #         self.c.execute(
    #             f"""
    #             UPDATE {product_type}
    #             SET offline = 1
    #             WHERE uuid in {tuple(uuids + [0])}  -- to remove a warning if tuple has one element (id,)
    #             """
    #         )

    def create_points_table(self):
        with self.conn:
            self.c.execute(
                """
                CREATE TABLE IF NOT EXISTS points
                (
                point_id INTEGER PRIMARY KEY,
                lat DOUBLE,
                lon DOUBLE,
                CONSTRAINT unq UNIQUE (lat, lon)
                ) 
                """
            )

    def insert_point(self, point):
        lat, lon = parse_point(point)
        with self.conn:
            self.c.execute(
                """
                INSERT OR IGNORE INTO points
                (lat, lon)
                VALUES (?, ?) 
                """,
                (lat, lon)
            )

    def count_points(self):
        self.c.execute("SELECT COUNT(1) FROM points")
        return self.c.fetchone()[0]

    def get_point_id(self, point):
        lat, lon = parse_point(point)
        self.c.execute(f"SELECT point_id FROM points WHERE lat = {lat} AND lon = {lon}")
        point_id = self.c.fetchone()
        if point_id is not None:
            point_id = point_id[0]
        return point_id
