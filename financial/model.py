from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class FinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<FinancialData(symbol='{self.symbol}', date='{self.date}', open_price='{self.open_price}', close_price='{self.close_price}', volume='{self.volume}')>"
