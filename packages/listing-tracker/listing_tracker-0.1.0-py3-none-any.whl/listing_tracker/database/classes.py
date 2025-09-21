from listing_tracker.database import connection

class Column: 
    def __init__(self, name: str, type: str, null: bool, default_val: str):
        self.name = name
        self.type = type
        self.null = "" if null else "NOT NULL"
        self.default_val = default_val
        self.column = f'{self.name} {self.type} {self.null} {self.default_val}'

class Table:
    def __init__(self, name: str):
        self.name = name
        self.columns = []

    def column_assign(self, columns):
        [self.columns.append(column) for column in columns]

    def get_dict(self):
        column_dicts = []
        for column in self.columns:
            column_dict = dict(column_name = column.name, column_type = column.type, column_null = column.null, column_default_val = column.default_val)
            column_dicts.append(column_dict)
        table_dict = dict(table_name = self.name, columns = column_dicts)
        return table_dict
    
    def exists(self):
        find = connection.cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{self.name}";')
        exists = True if len(find.fetchall()) > 0 else False
        return exists
    
    def create(self, table_dict):
        cursor_statement = f'CREATE TABLE {self.name}('
        for column in table_dict["columns"]:
            cursor_statement += f'{column["column_name"]} {column["column_type"]} {column["column_null"]} {column["column_default_val"]}'
            cursor_statement += ", " if column != table_dict["columns"][-1] else ")"
        connection.cursor.execute(cursor_statement)
    
    def insert(self, values: tuple):
        cursor_statement = f'INSERT INTO {self.name} VALUES{values};'
        connection.cursor.execute(cursor_statement)
        connection.db.commit()

    def insert_many(self, values: list[tuple]):
        cursor_statement = f'INSERT INTO {self.name} VALUES'
        for row in values:
            cursor_statement += f'{row}'
            cursor_statement += ", " if row != values[-1] else ";"
        connection.cursor.execute(cursor_statement)
        connection.db.commit()