"""Deterministic synthetic business data. Run with: python -m app.seed"""
from datetime import date, timedelta
from pathlib import Path
import random
from sqlalchemy import create_engine, text

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "business_performance.db"

SCHEMA = """
DROP TABLE IF EXISTS daily_metrics;
CREATE TABLE daily_metrics (
  metric_date TEXT PRIMARY KEY, revenue REAL NOT NULL, orders INTEGER NOT NULL,
  response_minutes REAL NOT NULL, csat REAL NOT NULL, fulfillment_rate REAL NOT NULL
);
"""

def seed(path=DB_PATH):
    path.parent.mkdir(exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    rng = random.Random(2027)
    with engine.begin() as conn:
        for statement in SCHEMA.strip().split(";"):
            if statement.strip(): conn.execute(text(statement))
        start = date(2027, 1, 1)
        for day in range(120):
            d = start + timedelta(days=day)
            weekly = 1.12 if d.weekday() in (0, 1) else .93
            incident = .78 if 70 <= day <= 76 else 1
            revenue = round((10200 + day * 22 + rng.gauss(0, 560)) * weekly * incident, 2)
            orders = int((138 + day * .25 + rng.gauss(0, 9)) * weekly * incident)
            response = round(42 + max(0, day - 65) * .45 + rng.gauss(0, 3), 1)
            csat = round(min(5, max(1, 4.47 - max(0, day - 65) * .012 + rng.gauss(0, .07))), 2)
            fulfillment = round(min(100, max(80, 96.2 - max(0, day - 65) * .12 + rng.gauss(0, .6))), 1)
            conn.execute(text("INSERT INTO daily_metrics VALUES (:d,:r,:o,:t,:c,:f)"),
              {"d":str(d),"r":revenue,"o":orders,"t":response,"c":csat,"f":fulfillment})
    return path

if __name__ == "__main__": print(seed())
