import os
import duckdb
import pandas as pd
from typing import Tuple, Optional, List, Any
from backend.config import log

class Database:
    def __init__(self, data_dir: str = "data"):
        self.conn = duckdb.connect(":memory:")
        self.data_dir = data_dir
        self._init_db()
    
    def _init_db(self):
        if not os.path.exists(self.data_dir):
            log("DB", f"Directory '{self.data_dir}' not found", "R")
            return
        
        try:
            self.conn.execute("INSTALL fts; LOAD fts;")
        except Exception as e:
            log("DB", f"Could not load FTS extension: {e}", "Y")

        files = [f for f in os.listdir(self.data_dir) if f.endswith('.parquet')]
        for f in files:
            name = f.replace('.parquet', '')
            path = os.path.join(self.data_dir, f)
            try:
                self.conn.execute(f"""
                    CREATE TABLE {name} AS 
                    SELECT * FROM read_parquet('{path}')
                """)
                
                if name == "diagnoses":
                    self.conn.execute(f"PRAGMA create_fts_index('diagnoses', 'diagnosis_code', 'diagnosis_name')")
                    log("DB", "Indexed 'diagnoses' for search", "G")
                elif name == "drugs":
                    self.conn.execute(f"PRAGMA create_fts_index('drugs', 'drug_id', 'full_name')")
                    log("DB", "Indexed 'drugs' for search", "G")

                    
            except Exception as e:
                log("DB", f"Error loading {f}: {e}", "R")
    
    def get_schema(self) -> str:
        try:
            tables = [t[0] for t in self.conn.execute("SHOW TABLES").fetchall()]
            out = []
            for t in tables:
                cols = self.conn.execute(f"DESCRIBE {t}").fetchall()
                col_str = ", ".join([f"{c[0]}:{c[1]}" for c in cols])
                out.append(f"TABLE {t} ({col_str})")
            return "\n".join(out)
        except:
            return "No tables found."

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Executes SQL and returns (DataFrame, ErrorString).
        ALWAYS returns a tuple of size 2.
        """
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        if any(w in sql.upper() for w in forbidden):
            return None, "Security Violation: Read-only access permitted."
        
        try:
            if params:
                df = self.conn.execute(sql, params).df()
            else:
                df = self.conn.execute(sql).df()
            return df, None
        except Exception as e:
            return None, str(e)
