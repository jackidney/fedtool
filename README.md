# CME Fedwatch Tool
This personal project is a Python3 Replication of the CME group's FedWatch Tool. The script is contained in file1.py.

I got a limited free trial subscription from a financial data vendor (barchart), so I only have intraday EFFR options data from May 14th, but the same farmework should still make correct calculations for a wider time frame.

The program seems to correctly calculate the market-implied probability of a fed cut using at the June meeting using the options data from that moment I downloaded it from the server midday (probability spreads vary somewhat intraday).

To do: 
-Make binary probabilities interpretable through a GUI (software currently prints to command line)
