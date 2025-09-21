from listing_tracker import dir
import sqlite3

db_name = "database.sqlite"
db_dir = dir.root_dir/"database"
db_path = db_dir/db_name
db = sqlite3.connect(db_path)
cursor = db.cursor()