# Finance-Bot Project
## Prebuild Steps:
### Creating .env file 
In the directory ```/worker``` there needs to be a .env file created with the following line of code:
```POLYGON_API=user_api_key```
The user must sign up for a Polygon.io API key for the stock data pull. Open source API-less packages such as yfinance and investpy were tried in development but both had reliability issues so an alternative with an API key is used. 

## Build
```docker-compose up --build```