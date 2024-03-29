import sqlite3


class Database:
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

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
                on_daac INT,
                CONSTRAINT unq UNIQUE(uuid, point_id)
                ) 
                """
            )

    def insert_images(self, results, product_type):
        with self.conn:
            self.c.executemany(
                f"""
                INSERT OR IGNORE INTO {product_type}
                (uuid, name, datetime, size, point_id) 
                VALUES (?, ?, ?, ?, ?)
                """,
                zip(results['uuids'], results['names'], results['dates'], results['sizes'], results['point_id'])
            )

    def select_uuids_names(self, product_type, period=None, names=None):
        q = f"SELECT uuid, name FROM {product_type}"
        if names is not None and len(names) == 1:
            names = list(names) + ['']  # otherwise sqlite 'IN' fails
        if period is not None:
            date_start, date_end = period
            q += f" WHERE datetime BETWEEN '{date_start}' AND '{date_end}'"
            if names is not None:
                q += f" AND name IN {tuple(names)}"
        elif names is not None:
            q += f" WHERE name IN {tuple(names)}"
        if 'WHERE' in q:
            q += " AND loaded IS NULL"
        else:
            q += " WHERE loaded IS NULL"
        self.c.execute(q)
        return self.c.fetchall()

    def set_on_daac(self, product_type, uuid):
        with self.conn:
            self.c.execute(
                f"""
                UPDATE {product_type}
                SET on_daac = 1
                WHERE uuid = '{uuid}'
                """
            )

    def set_loaded(self, product_name, product_type):
        with self.conn:
            self.c.execute(
                f"""
                UPDATE {product_type}
                SET loaded = 1
                WHERE name = '{product_name}' 
                """
            )

    def set_offline(self, product_type, uuid):
        with self.conn:
            self.c.execute(
                f"""
                UPDATE {product_type}
                SET offline = 1
                WHERE uuid = '{uuid}'
                """
            )

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
        lat, lon = point
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
        lat, lon = point
        self.c.execute(f"SELECT point_id FROM points WHERE lat = {lat} AND lon = {lon}")
        point_id = self.c.fetchone()
        if point_id is not None:
            point_id = point_id[0]
        return point_id
