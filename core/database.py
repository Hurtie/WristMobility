from datetime import datetime
import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_path="diagnostics.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS Patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL
                    )
                """)

        self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS DiagnosticResults (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        patient_id INTEGER NOT NULL,
                        result TEXT NOT NULL,
                        FOREIGN KEY (patient_id) REFERENCES Patients (id)
                    )
                """)
        self.conn.commit()

    def get_or_create_patient(self, name):
        cursor = self.conn.execute("SELECT id FROM Patients WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor = self.conn.execute("INSERT INTO Patients (name) VALUES (?)", (name,))
            self.conn.commit()
            return cursor.lastrowid

    def save_diagnostic_result(self, patient_id, result_data):
        date_str = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO DiagnosticResults (date, patient_id, result) VALUES (?, ?, ?)",
            (date_str, patient_id, result_data)
        )
        self.conn.commit()
        return True

    def get_all_patients(self):
        cursor = self.conn.execute("SELECT id, name FROM Patients")
        return cursor.fetchall()

    def get_diagnostic_results_by_patient(self, patient_id):
        cursor = self.conn.execute(
            "SELECT id, date, result FROM DiagnosticResults WHERE patient_id = ? ORDER BY date DESC",
            (patient_id,)
        )
        results = []
        for row in cursor:
            results.append({
                'id': row[0],
                'date': row[1],
                'result': row[2]
            })
        return results

    def close(self):
        self.conn.close()