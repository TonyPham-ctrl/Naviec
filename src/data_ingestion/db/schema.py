from data_ingestion.db.connection import get_connection

CREATE_DISPATCH_PRICES_TABLE = """
CREATE TABLE IF NOT EXISTS dispatch_prices (
    settlementdate TIMESTAMP NOT NULL,
    regionid TEXT NOT NULL,
    rrp NUMERIC NOT NULL,
    PRIMARY KEY (settlementdate, regionid)
);
"""


def create_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_DISPATCH_PRICES_TABLE)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
