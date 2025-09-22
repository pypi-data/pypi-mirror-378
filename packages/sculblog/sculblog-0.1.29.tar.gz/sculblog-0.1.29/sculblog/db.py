import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Any, Optional

class DbConn:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_single_query(self, query, params=None):
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return None
    
    def insert_row(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self._get_connection() as conn:
            try:
                with conn:
                    conn.execute(query, tuple(data.values()))
                return True
            except sqlite3.Error as e:
                print(f"Insert error: {e}")
                return False
    
    def value_in_column(self, table, column, target):
        return bool(self.execute_single_query(f"SELECT 1 FROM {table} WHERE {column} = ?", (target,)))
    
    def update_row(self, table, where_column, where_value, update_columns):
        if not update_columns:
            return
        
        set_clause = ", ".join([f"{col} = ?" for col in update_columns.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_column} = ?"
        
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, (*update_columns.values(), where_value))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Update error: {e}")
    
    def execute_query(self, query, params=None):
        with self._get_connection() as conn:
            try:
                if conn.row_factory != sqlite3.Row:
                    conn.row_factory = sqlite3.Row
                with conn:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return []