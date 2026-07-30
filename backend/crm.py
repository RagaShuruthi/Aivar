import sqlite3
import os
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")

class MockCRM:
    """
    Mock CRM Database Manager storing 20 predefined customer records.
    Exposes Read, Update, and Delete operations for governed AI tool execution.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            # Drop old schema if columns differ
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(customers)")
                columns = [col[1] for col in cursor.fetchall()]
                if "department" not in columns or "role" not in columns:
                    cursor.execute("DROP TABLE customers")
                    conn.commit()

            conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    city TEXT NOT NULL,
                    department TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Seed 20 predefined customers if table is empty
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            if count == 0:
                sample_customers = [
                    (101, "Shruthi", "shruthi@crm.com", "+1-555-0101", "Boston", "Support", "support_agent", "Active VIP"),
                    (102, "Kavin", "kavin@crm.com", "+1-555-0102", "Seattle", "Sales", "sales_agent", "Active"),
                    (103, "Sabari", "sabari@crm.com", "+1-555-0103", "Austin", "Finance", "support_agent", "Active VIP"),
                    (104, "Elaki", "elaki@crm.com", "+1-555-0104", "San Jose", "HR", "support_agent", "Active"),
                    (105, "Harini", "harini@crm.com", "+1-555-0105", "Chicago", "Sales", "sales_agent", "Active VIP"),
                    (106, "Vignesh", "vignesh@crm.com", "+1-555-0106", "New York", "Support", "support_agent", "Active"),
                    (107, "Akash", "akash@crm.com", "+1-555-0107", "Atlanta", "Sales", "sales_agent", "Active"),
                    (108, "Priya", "priya@crm.com", "+1-555-0108", "Denver", "HR", "support_agent", "Active"),
                    (109, "Naveen", "naveen@crm.com", "+1-555-0109", "San Francisco", "Finance", "support_agent", "Active VIP"),
                    (110, "Keerthana", "keerthana@crm.com", "+1-555-0110", "Dallas", "Support", "support_agent", "Active"),
                    (111, "Rahul", "rahul@crm.com", "+1-555-0111", "Los Angeles", "Sales", "sales_agent", "Active VIP"),
                    (112, "Nisha", "nisha@crm.com", "+1-555-0112", "Miami", "Support", "support_agent", "Active"),
                    (113, "Dinesh", "dinesh@crm.com", "+1-555-0113", "Phoenix", "Manager", "sales_agent", "Active VIP"),
                    (114, "Kavya", "kavya@crm.com", "+1-555-0114", "Portland", "Support", "support_agent", "Active"),
                    (115, "Arjun", "arjun@crm.com", "+1-555-0115", "San Diego", "Sales", "sales_agent", "Active VIP"),
                    (116, "Deepika", "deepika@crm.com", "+1-555-0116", "Seattle", "Finance", "support_agent", "Active"),
                    (117, "Sanjay", "sanjay@crm.com", "+1-555-0117", "Houston", "Support", "support_agent", "Active"),
                    (118, "Meena", "meena@crm.com", "+1-555-0118", "Detroit", "HR", "support_agent", "Active"),
                    (119, "Ashwin", "ashwin@crm.com", "+1-555-0119", "Minneapolis", "Sales", "sales_agent", "Active VIP"),
                    (120, "Divya", "divya@crm.com", "+1-555-0120", "Raleigh", "Admin", "admin_agent", "Active Admin"),
                ]
                cursor.executemany(
                    "INSERT INTO customers (id, name, email, phone, city, department, role, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    sample_customers
                )
                conn.commit()

    def get_all_customers(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def read_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_customer(self, customer_id: int, field: str, value: str) -> Optional[Dict[str, Any]]:
        valid_fields = {"name", "email", "phone", "city", "department", "status"}
        if field not in valid_fields:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE customers SET {field} = ? WHERE id = ?", (value, customer_id))
            conn.commit()
            return self.read_customer(customer_id)

    def delete_customer(self, customer_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            return cursor.rowcount > 0

# Instantiated Singleton CRM Instance
crm_db = MockCRM()
