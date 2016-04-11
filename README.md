# quoteService
Simple twilio app to service quote information 

A flask app that listens for sms requests and returns with quote information.

To use, text the number with a symbol prefixed with $. Ex. $MSFT 

Commands: 
$SYMBOL -> Retrieves any tickers in the message prefixed with $. Multiple symbols can be retrieved by entering more than one symbol.
Spaces can be used as optional separators for easy of use. 
Ex. to find the quote for Microsoft, send $MSFT. 
For Microsoft and Apple, send $MSFT$AAPL or $MSFT $AAPL
Sending asd$AAPL will result in $AAPL being returned and the prefix before $ being thrown away.
Symbols are case insensitive.

help -> To access the unsubscribe menu

last -> repeats the last query

Entering a text string that does not contain $ and is not a command will result in the help message.

Before running the app, rename the example.json file to config.json. Currently, the twilio keys are not used so they can be left blank.

Data is retrieved through the public markitondemand demo API. For production use, a non rate limited API would be needed. One would just need to implement a function to replace get_stock_quote_markit.

TODOS:

Implement unit tests for functions. Modularize functions. 
