import requests

from datetime import datetime, timedelta
from flask import Flask, current_app
from financial.model import db, FinancialData
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config.from_object("financial.config.Config")

db.init_app(app)


# Retrieves the financial data of the given symbol and store it to the data base
def fetch_and_store_data(symbol: str, weeks: int) -> None:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={current_app.config['ALPHAVANTAGE_API_KEY']}"
    response = requests.get(url)

    if response.status_code == 200:
        fin_data = response.json()['Time Series (Daily)']

        for date_str, values in fin_data.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # As we need only the data of the last two weeks, filter data by the date:
            if date >= datetime.today().date() - timedelta(weeks = weeks):
                open_price = float(values['1. open'])
                close_price = float(values['4. close'])
                volume = int(values['6. volume'])

                # Duplicated records should be avoided, 
                # so first check if the data for this date and symbol is exists in our table:
                record = db.session.execute(db.select(FinancialData)
                                         .where(FinancialData.symbol == symbol)
                                         .where(FinancialData.date == date)
                                         ).first()
                if not record:
                    record = FinancialData(
                        symbol = symbol,
                        date = date,
                        open_price = open_price,
                        close_price = close_price,
                        volume = volume
                    )
                    db.session.add(record)

    db.session.commit()


def retrieve_data(weeks: int = 2, clear: bool = False) -> str:
    db.create_all()
    message = ""

    if clear:
        db.session.execute(db.delete(FinancialData))
        db.session.commit()
        message = "Table has been emptied. "

    if weeks < 1:
        weeks = 0

    # for the testing purposes we can leave the table empty:
    if weeks == 0:
        return message + "No data has been added to the database.\n"

    try:
        symbols = ['IBM', 'AAPL']
        for symbol in symbols:
            fetch_and_store_data(symbol, weeks)

        print(FinancialData.query.all())

    except SQLAlchemyError as e:
        return message +  f"Failed to insert data into the database [{e}].\n"

    return message + f"Successfully fetched and stored IBM and Apple stock data for the last {weeks} weeks\n"



if __name__ == '__main__':
    with app.app_context():
        res = retrieve_data()
        print(res)