import math
import os
import http.client

from datetime import datetime
from financial.v1.messages import Message
from flask import Blueprint, current_app, jsonify, request
from get_raw_data import retrieve_data
from financial.model import db, FinancialData


api = Blueprint('api', __name__)

page_size_default = 5
page_default = 1


# Root of the app
@api.route("/")
def financial_home() -> str:
    return Message.HELLO.value



# For easy retrieve the data from the Alpha Vantage API
@api.route("/retrieve", methods=['GET'])
def retrieve() -> str:
    clear = int(request.args.get('clear', 0)) # 1 for testing purposes
    weeks = int(request.args.get('weeks', 2)) # 0 for leaving the table empty for testing purposes

    clear = True if clear > 0 else False

    return retrieve_data(weeks, clear), http.client.OK



# Get records from financial_data table
@api.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    try:
        # parse input parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', page_size_default))
        page = int(request.args.get('page', page_default))

        # validate input parameters
        if start_date and end_date and start_date > end_date:
            raise ValueError(Message.DATE_RANGE_INCORRECT.value)

        query = FinancialData.query
        query = query.order_by(FinancialData.date)

        # optional conditions:
        if symbol:
            query = query.filter(FinancialData.symbol == symbol)
        if start_date:
            query = query.filter(FinancialData.date >= start_date)
        if end_date:
            query = query.filter(FinancialData.date <= end_date)      

        # pagination
        total_count = query.count()
        total_pages = math.ceil(total_count / limit)

        if page > total_pages:
            raise ValueError(Message.PAGE_COUNT_ERROR.value)

        data = query.paginate(page=page, per_page=limit)
        
        # format the response
        response_data = [{
            'symbol': item.symbol,
            'date': item.date.strftime('%Y-%m-%d'),
            'open_price': str(item.open_price),
            'close_price': str(item.close_price),
            'volume': str(item.volume)
        } for item in data.items]

        response_pagination = {
            'count': total_count,
            'page': page,
            'limit': limit,
            'pages': total_pages
        }
        
        response_info = {'error': ''}
        response_status = http.client.OK

    except Exception as e:
        response_data = []
        response_pagination = {'count': 0, 'page': 0, 'limit': 0, 'pages': 0}
        response_info = {'error': str(e)}
        response_status = http.client.BAD_REQUEST

    return jsonify({'data': response_data, 'pagination': response_pagination, 'info': response_info}), response_status




# Get the statistics of the financial_data table
@api.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        # parse input parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        symbols = request.args.getlist('symbol')

        # validate input parameters
        if start_date is None or end_date is None or not symbols:
            raise ValueError(Message.DATE_REQUIRED_ERROR.value)
        
        if start_date > end_date:
            raise ValueError(Message.DATE_RANGE_INCORRECT.value)

        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        # query the DB for the relevant data
        query = db.session.query(
            db.func.avg(FinancialData.open_price).label('avg_open_price'),
            db.func.avg(FinancialData.close_price).label('avg_close_price'),
            db.func.avg(FinancialData.volume).label('avg_volume')
        ).filter(
            FinancialData.symbol.in_(symbols),
            FinancialData.date >= start_date,
            FinancialData.date <= end_date
        ).first()
        
        # format the response
        response_data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'symbols': symbols,
            'average_daily_open_price': round(query.avg_open_price, 2),
            'average_daily_close_price': round(query.avg_close_price, 2),
            'average_daily_volume': int(round(query.avg_volume))
        }
        response_info = {'error': ''}
        response_status = http.client.OK
    
    except Exception as e:
        response_data = {}
        response_info = {'error': str(e)}
        response_status = http.client.BAD_REQUEST
    
    return jsonify({'data': response_data, 'info': response_info}), response_status
