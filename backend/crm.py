import sqlite3
import os
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")

class MockCRM:
    """
    Mock CRM Database Manager storing 20 enterprise customer profiles.
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    city TEXT NOT NULL,
                    company TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Seed 20 customers if table is empty
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            if count == 0:
                sample_customers = [
                    (101, "Alice Smith", "alice@acmecorp.com", "+1-555-0101", "New York", "Acme Corp", "Active VIP"),
                    (102, "Bob Jones", "bob@globex.com", "+1-555-0102", "San Francisco", "Globex Corp", "Active"),
                    (103, "Charlie Brown", "charlie@stark.com", "+1-555-0103", "Chicago", "Stark Industries", "Active VIP"),
                    (104, "Diana Prince", "diana@themyscira.com", "+1-555-0104", "Washington DC", "Wayne Ent", "Pending"),
                    (105, "Evan Wright", "evan@cyberdyne.com", "+1-555-0105", "Los Angeles", "Cyberdyne", "Active"),
                    (106, "Fiona Gallagher", "fiona@omnicorp.com", "+1-555-0106", "Detroit", "OmniCorp", "Active"),
                    (107, "George Clark", "george@initech.com", "+1-555-0107", "Austin", "Initech", "Active"),
                    (108, "Hannah Abbott", "hannah@hooli.com", "+1-555-0108", "Palo Alto", "Hooli", "Inactive"),
                    (109, "Ian Malcolm", "ian@ingen.com", "+1-555-0109", "Costa Rica", "InGen", "Active VIP"),
                    (110, "Julia Roberts", "julia@massive.com", "+1-555-0110", "Seattle", "Massive Dynamic", "Active"),
                    (111, "Kevin Flynn", "kevin@encom.com", "+1-555-0111", "Boston", "ENCOM", "Active VIP"),
                    (112, "Laura Croft", "laura@manor.com", "+1-555-0112", "London", "Croft Holdings", "Active VIP"),
                    (113, "Michael Scott", "michael@dundermifflin.com", "+1-555-0113", "Scranton", "Dunder Mifflin", "Active"),
                    (114, "Nina Williams", "nina@mishima.com", "+1-555-0114", "Tokyo", "Mishima Zaibatsu", "Active"),
                    (115, "Oscar Martinez", "oscar@accounting.com", "+1-555-0115", "Philadelphia", "Vance Refrigeration", "Active"),
                    (116, "Peter Parker", "peter@dailybugle.com", "+1-555-0116", "New York", "Oscorp", "Active"),
                    (117, "Quinn Fabray", "quinn@mckinley.com", "+1-555-0117", "Lima", "McKinley", "Pending"),
                    (118, "Rachel Green", "rachel@ralphlauren.com", "+1-555-0118", "New York", "Ralph Lauren", "Active"),
                    (119, "Steve Rogers", "steve@avengers.com", "+1-555-0119", "Brooklyn", "Shield", "Active VIP"),
                    (120, "Tony Stark", "tony@stark.com", "+1-555-0120", "Malibu", "Stark Tech", "Active VIP"),
                ]
                cursor.executemany(
                    "INSERT INTO customers (id, name, email, phone, city, company, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
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
        valid_fields = {"name", "email", "phone", "city", "company", "status"}
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
