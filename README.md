# Financial Data

## Retrieving the financial data of two given stocks (IBM, Apple Inc.)
For retrieving the data [AlphaVantage](https://www.alphavantage.co/documentation/) API is used.
For using AlphaVantage API you should [get the API key](https://www.alphavantage.co/support/#api-key) and save it to the **.env** file in the project root directory.
API key of the production environment should be saved in the **.env.production file**: this file will be copied due to docker container building process to the production root folder as .env file.

There is my own API key listed in both .env and .env.production files. As this key is for testing purposes only and doesn't have a secret meaning, please feel free to use it for testing my task assignment. But for real server you should get your own API keys.


## Developing mode
For developing purpose we should install [Flask](https://flask.palletsprojects.com/en/2.2.x/), and also [pipenv](https://pipenv.pypa.io/en/latest/) for dependency managing.

If no .env file is in the project root directory, please dublicate the env.sample file, rename it to .env, and specify the ALPHAVANTAGE_API_KEY parameter in it.

Then from the application root directory run:
```
./dev_entrypoint.sh
```
Developing server works on 5000 port:
```
curl http://127.0.0.1:5000/
```


## Production server building
To quick launch the production version we use the Docker container on a **python2.8-alpine** image with **nginx** installed additionally.
uWSGI is used for serving Flask application. The API production server listens to a 80 port.


### The very first launch

For building an image at the first time:

```
make build
```


### To stop the server

```
make stop
```


### To start server again

```
make start
```


## How to use this API

### First retrieve the stock data and save it to the database
For retrieving the stock data with the AlphaVantage API one can make a request to the /retrieve endpoint.
By default the data of the most recently 2 weeks will be retrieved and stored to the data base.
Duplicated records will be avoided when executing retrieving multiple times.

```
curl http://localhost/retrieve
```

**For testing purposes** you can clear all the data from the table by providing a _clear_ parameter:
```
curl http://localhost/retrieve?clear=1
```

Also you can provide a _weeks_ parameter for specify a weeks amount data should be retrieved for (if not providing, 2 weks will be used by default):
```
curl http://localhost/retrieve?weeks=20
```
This will show the message: **Successfully fetched and stored IBM and Apple stock data for the last 20 weeks**

For testing purposes you can clear all the data from the table and don't add any data to it: 
```
curl "http://localhost/retrieve?clear=1&weeks=0"
```
This request will emptied a table at all. After this request you should add the data to the table again by requesting a `curl http://localhost/retrieve`.
The message returned: **Table has been emptied. No data has been added to the database**



### Get financial_data
```
curl http://localhost/api/financial_data
```
This endpoint accepts following parameters: **start_date**, **end_date**, **symbol**. All parameters are optional.
The endpoint also supports pagination with parameters: **limit** and **page**. If no pagination parameters are given, default limit for one page is 5, page is 1.

Sample request (replace values by correct ones):
```
curl "http://localhost/api/financial_data?start_date=2023-03-01&end_date=2023-03-17&symbol=AAPL&limit=5&page=3"
```
Sample response:
```
{
  "data": [
    {
      "symbol": "AAPL",
      "date": "2023-03-15",
      "open_price": "151.19",
      "close_price": "152.99",
      "volume": "77167866"
    },
    {
      "symbol": "AAPL",
      "date": "2023-03-16",
      "open_price": "152.16",
      "close_price": "155.85",
      "volume": "76254419"
    },
    {
      "symbol": "AAPL",
      "date": "2023-03-17",
      "open_price": "156.08",
      "close_price": "155.0",
      "volume": "98944633"
    }
  ],
  "pagination": {
    "count": 13,
    "page": 3,
    "limit": 5,
    "pages": 3
  },
  "info": {
    "error": ""
  }
}
```


### Get statistics
```
curl http://localhost/api/statistics
```
This endpoint accepts following parameters: **start_date**, **end_date**, **symbol**. All parameters are required.

Sample request (replace values by correct ones):
```
curl "http://localhost/api/statistics?start_date=2023-03-01&end_date=2023-03-17&symbol=IBM&symbol=AAPL"
```
Sample response:
```
{
  "data": {
    "start_date": "2023-03-01",
    "end_date": "2023-03-17",
    "symbols": [
      "IBM",
      "AAPL"
    ],
    "average_daily_open_price": 138.96,
    "average_daily_close_price": 138.97,
    "average_daily_volume": 38431428
  },
  "info": {
    "error": ""
  }
}
```



## About this API

### Why Flask?
Flask developers call it a "microframework", what means that the core is simple but extensible.
For such simple tasks as a file storage service, it is best suited: all the necessary functionality is present without overloading with unnecessary modules.

### Why SQLite
This application uses a SQLite database to store financial data. Python comes with built-in support for SQLite in the sqlite3 module.
SQLite is convenient because it doesn’t require setting up a separate database server and is built-in to Python.

### Why pipenv but not requirements.txt file (about virtual environments)
It's true that pip supports package management through the requirements.txt file, but this tool lacks some features required on serious projects running on different production and development machines. Among its issues, the ones that cause the most problems are:

- pip installs packages globally, making it hard to manage multiple versions of the same package on the same machine.
- requirements.txt need all dependencies and sub-dependencies listed explicitly, a manual process that is tedious and error-prone.

To solve these issues, we are using **pipenv**. Pipenv is a dependency manager that isolates projects in private environments, allowing packages to be installed per project.


## Versioning
Sometimes we need to change a functionality, so the prevoius functionally is totally breaks. We must to provide a reliable and efficient service for users. That is why we always should be sure that our API is up-to-date and bug-free. This is why we use versioning in our API.

The requests to the server without a version mark references to the last version of the API. So as current last version is v1, the request:
```
curl http://localhost/
```
if the same as:
```
curl http://localhost/v1/
```

### Why Versioning is Important
1. **Backwards Compatibility**: By versioning our API, we are able to ensure that previous versions of the API will continue to work as expected. This means that if a user is using an older version of the API (i.e. an older version ov CLI application), they will not be affected by any changes made to the newer versions.

2. **Testing**: Versioning allows us to test new features and changes in a controlled environment before releasing them to the public. This means that we can ensure that the new version of the API is stable and reliable before making it available to our users.

### How to implement versioning in this API

One way to achieve this is by creating a new folder for the new version within the **api** directory. For example, if we are creating version 2 of the API, we would create a new folder named "v2" within the *financial* directory, and then we would implement all of the new functionality and changes. Additionally we would add some directives to filestorage/\_\_init\_\_.py file.
This allows us to keep the new version separate from the previous version, making it easy to maintain and test.