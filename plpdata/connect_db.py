import psycopg


'''
password=password,
    host=host,
    port=port
'''
with psycopg.connect("dbname=postgres user=postgres password=password host=localhost port=5432") as conn:

    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        # # Execute a command: this creates a new table
        # cur.execute("""
        #     CREATE TABLE test (
        #         id serial PRIMARY KEY,
        #         num integer,
        #         data text)
        #     """)

        # # Pass data to fill a query placeholders and let Psycopg perform
        # # the correct conversion (no SQL injections!)
        # cur.execute(
        #     "INSERT INTO team (city, sponsor, name) VALUES (%s, %s, %s)",
        #     ("taipei", "fubon", "braves"))

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM team")
        # cur.fetchall()
        # will return (1, 100, "abc'def")

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        for record in cur.fetchall():
            print(record)

