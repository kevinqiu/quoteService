# quoteService
Simple twilio app to service quote information 

A flask app that listens for sms requests and returns with quote information.

To use, text the number with $SYMBOL. 

Commands: 
$SYMBOL -> Retrieves any tickers in the message prefixed with $. Multiple symbols can be retrieved by entering more than one symbol.
Spaces can be used as optional separators for easy of use. 
Ex. to find the quote for Microsoft, send $MSFT. 
For Microsoft and Apple, send $MSFT$AAPL or $MSFT $AAPL
Sending asd$AAPL will result in $AAPL being returned and the prefix before $ being thrown away.

help -> To access the unsubscribe menu

last -> repeats the last query

Entering a text string that does not contain $ and is not a command will result in the help message.