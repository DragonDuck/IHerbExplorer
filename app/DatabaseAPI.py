import sqlite3
import pandas as pd


def get_items(category=None, table="iherb", db_name="databases/items.db"):
    """
    Extract items from a database. Optionally, only items of a certain category will be extracted.

    :param category: Item category to filter for
    :param table: Table to read from
    :param db_name: The path to the SQLite file
    :return: A list of tuples (item_id, item_name)
    """

    # Build query
    query = "SELECT * FROM {}".format(table)

    if category is not None:
        query += " WHERE category LIKE '%{}%'".format(category)

    con = sqlite3.connect(db_name)
    items = pd.read_sql_query(query, con)
    con.close()

    return items


def get_categories(table="iherb", db_name="databases/items.db"):
    """
    Lightweight function to extract only the unique super-categories

    :param table: Table to read from
    :param db_name: The path to the SQLite file
    :return:
    """

    query = "SELECT DISTINCT category FROM {}".format(table)

    con = sqlite3.connect(db_name)
    cur = con.cursor()
    items = list(set([item[0].split(",")[0] for item in cur.execute(query).fetchall()]))
    con.close()

    return items
