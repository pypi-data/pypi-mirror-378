from listing_tracker import database
import datetime
import os
import re
classes = database.classes
connection = database.connection
datetime_type = datetime.datetime

listings_table = classes.Table("listings")
listings_table.column_assign([classes.Column("link", "text", False, ""),
    classes.Column("website", "text", True, f'{None}'),
    classes.Column("init_datetime", "blob", False, "")])
listings_table_dict = listings_table.get_dict()
if not listings_table.exists():
    listings_table.create(listings_table_dict)

if not os.path.exists(connection.db_path):
    listings_table.create(listings_table_dict)

def website_identifier(url):
    url = re.sub(r'http[s]?://', "", url)
    domain = re.sub(r'/.*', "", url)
    websites = connection.cursor.execute("SELECT * FROM websites").fetchall()
    for website in websites:
        if domain == website[1]:
            return website[0]
    return "null"

def datetime_adapter(datetime):
    return datetime.isoformat()

def add_listing(listings_table: classes.Table, url):
    website = website_identifier(url)
    init_datetime = datetime_type.now(datetime.timezone.utc).replace(microsecond=0)
        # 'datetime.timezone.utc' is used instead of 'datetime.UTC' to
        # support Python 3.10
    values = (url, website, datetime_adapter(init_datetime))
    listings_table.insert(values)
    log_message = f'Listing from {website} successfully inserted' if website != "null" else f'Listing {url} successfully inserted'
    print(log_message)