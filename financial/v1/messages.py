from enum import Enum

class Message(Enum):
    HELLO = "Hello! This is a program that retrieves IBM and Apple stock data."
    DATE_RANGE_INCORRECT = 'An end_date must be more or equal than a start_date'
    DATE_REQUIRED_ERROR = 'Please specify all the required parameters: start_date, end_date and at least one symbol from [IBM, AAPL] as symbol.'
    PAGE_COUNT_ERROR = 'This page is not exists within the specified conditions'
