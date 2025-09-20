# Firstock Connect API Python Client 

The official Python library for the Firstock Connect API, providing a seamless interaction with Firstock's trading and financial data services. This library has been designed for developers to easily integrate Firstock's advanced trading capabilities into their Python applications.

## Features

- HTTP calls are converted to methods.
- JSON responses are wrapped into Python-compatible objects.
- The handling of WebSocket connections is automated.

## Installation
This module is installed via pip:
```python
pip install firstock
```

## Getting started with API
The API consists of five major section 
* Login & Profile
* Orders & Report
* Market Connect

### Login
For the Login process we require to generate the appkey and vendor code by logging in with the firstock credentials in the give link [Key Generation](https://firstock.in/api/docs/login/).

```python
from firstock import firstock

login = firstock.login(
    userId="{{userID}}",
    password="{{Password}}",
    TOTP="{{TOTP}}",
    vendorCode="{{vendorCode}}",
    apiKey="{{apiKey}}",
  )
```
### Logout
```python
from firstock import firstock

logout = firstock.logout(userId="{{userId}}")
```
### User Details
```python
from firstock import firstock

userDetails = firstock.userDetails(userId="{{userId}}")
```

### Place Order

```python
from firstock import firstock

placeOrder = firstock.placeOrder(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="ITC-EQ",
    quantity="1",
    price="300",
    product="I",
    transactionType="B",
    priceType="LMT",
    retention="DAY",
    triggerPrice="0",
    remarks="Python Package Order"
)
```
### Order Margin
```python
from firstock import firstock

orderMargin = firstock.orderMargin(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="ITC-EQ",
    quantity="1",
    priceType="LMT",
    product="C",
    price="350",
    transactionType="B"
)
```

### Order Book
```python
from firstock import firstock

orderBook = firstock.orderBook(userId="{{userId}}")
```
### Cancel Order
```python
from firstock import firstock

cancelOrder = firstock.cancelOrder(
    userId="{{userId}}",
    orderNumber="25063000011862"
)
```
### Modify Order
```python
from firstock import firstock

modifyOrder = firstock.modifyOrder(
    userId="{{userId}}",
    orderNumber="25070100015934",
    quantity="1",
    price="418",
    triggerPrice="0",
    tradingSymbol="IDEA-EQ",
    priceType="LMT",
    retention="DAY",
    mkt_protection="0.5",
    product="C"
)
``` 
### Single Order History
```python
from firstock import firstock

singleOrderHistory = firstock.singleOrderHistory(
    userId="{{userId}}",
    orderNumber="25063000011911"
)
```

### Trade Book
```python
from firstock import firstock

tradeBook = firstock.tradeBook(userId="{{userId}}")
```

### Position Book
```python
from firstock import firstock

positionBook = firstock.positionBook(userId="{{userId}}")
```

### Convert Product
```python
from firstock import firstock

convertProduct = firstock.productConversion(
    userId="{{userId}}",
    transactionType="B",
    tradingSymbol="ITC-EQ",
    quantity="1",
    product="C",
    previousProduct="I",
    positionType="DAY",
    exchange="NSE"
)
```
### Holdings
```python
from firstock import firstock

holdings = firstock.holdings(userId="{{userId}}")
```
### Limits
```python
from firstock import firstock

limits = firstock.limit(userId="{{userId}}")
```
### Basket Margin
```python
from firstock import firstock

basketMargin = firstock.basketMargin(
    userId="{{userId}}",
    exchange="NSE",
    transactionType="B",
    product="C",
    tradingSymbol="RELIANCE-EQ",
    quantity="1",
    priceType="MKT",
    price="0",
    BasketList_Params=[
        {
            "exchange": "NSE",
            "tradingSymbol": "IDEA-EQ",
            "quantity": "1",
            "transactionType": "B",
            "price": "0",
            "product": "C",
            "priceType": "MKT"
        }
    ]
)
```
### Get Security Info
```python
from firstock import firstock

getSecurityInfo = firstock.securityInfo(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="NIFTY"
)
```

### Get Quote
```python
from firstock import firstock

getQuotes = firstock.getQuote(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="NIFTY"
)
```
### Get Index List
```python
from firstock import firstock

getIndexList = firstock.indexList(userId="{{userId}}")
```

### Option Chain
```python
from firstock import firstock

optionChain = firstock.optionChain(
    userId="{{userId}}",
    exchange="NFO",
    symbol="NIFTY",
    strikePrice="23150",
    expiry="03JUL25",
    count="5"
)
```

### Search Scrips
```python
from firstock import firstock

searchScrips = firstock.searchScrips(
    userId="{{userId}}",
    stext="ITC"
)
```

### Get Quote LTP
```python
from firstock import firstock

getQuoteLtp = firstock.getQuoteltp(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="RELIANCE-EQ"
)
```
### Get Multi Quote
```python
from firstock import firstock

multiQuote = firstock.getMultiQuotes(
    userId="{{userId}}",
    dataToken=[
        {
            "exchange": "NSE",
            "tradingSymbol": "Nifty 50"
        },
        {
            "exchange": "NFO",
            "tradingSymbol": "NIFTY03APR25C23500"
        }
    ]
)
```
### Get Multi Quote LTP
```python
from firstock import firstock

multiQuoteLtp = firstock.getMultiQuotesltp(
    userId="{{userId}}",
    dataToken=[
        {
            "exchange": "NSE",
            "tradingSymbol": "Nifty 50"
        },
        {
            "exchange": "NSE",
            "tradingSymbol": "Nifty Bank"
        }
    ]
)
```
### Brokerage Calculator
```python
from firstock import firstock

brokerageCalc = firstock.brokerageCalculator(
    userId="{{userId}}",
    exchange="NFO",
    tradingSymbol="RELIANCE27FEB25F",
    transactionType="B",
    product="M",
    quantity="500",
    price="125930",
    strike_price="0",
    inst_name="FUTSTK",
    lot_size="1"
)
```
### Get Expiry
```python
from firstock import firstock

getExpiry = firstock.getExpiry(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="NIFTY"
)
```
### Time Price Series
```python
from firstock import firstock

timePriceSeries = firstock.TimePriceSeries(
    userId="{{userId}}",
    exchange="NSE",
    tradingSymbol="Nifty 50",
    startTime="13/02/2023 09:45:45",
    endTime="13/12/2023 13:56:34",
    interval="30"
)
```

### Get Holdings Details
```python
from firstock import firstock

holdings_details = firstock.getHoldingsDetails(
    userId="{{userId}}"
)
```

Refer to the Firstock Connect Documentation for the complete list of supported methods.


## Changelog
* The Python package has been updated to automatically convert passwords into SHA256 hashes prior to submission to the login URL. 


* The package now includes a multi-login feature, enabling simultaneous login for multiple users, with each user's session being individually stored. 


* For all APIs, it is now required to pass the userId. The corresponding jKey session linked to the userId will be utilized for executing the API.


* The following methods have been updated to require trading symbols instead of tokens:
  * Get Multi Quotes LTP 
  * Get Multi Quotes 
  * Day Interval Time Price Series 
  * Time Price Series 
  * Security Info 
  * Get Quotes 


* The method for accessing the websocket has been entirely revamped. Detailed information will be available in an upcoming blog post. Additionally, sample code illustrating the new method can be found in the examples section.

## [1.0.2] - 2025-08-14
### Changed
- Minor version bump for compatibility updates.