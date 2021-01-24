# Willys pricehunter

The Willys pricehunter tracks food prices and discounts over time. The project consists of a toy database (a json dict dump) that is created and updated by `scanner.py`. The scanner fetches the latest prices of all Willys products and keeps track of price changes over each new week. All price data is visualized in the fastapi frontend `main.py`. 

# Deploy

1. Clone repo to /opt/
2. `$ mkdir /home/ubuntu/database`
3. Run scanner to initialize database: `$ python3 /opt/willys-pricehunter/app/scanner.py`
4. Run frontend: `$ sh /opt/willys-pricehunter/run.sh`

To get continuous price history, the scanner can be executed once per day by setting a crontab job:

```
0 7 * * * /usr/bin/python3 /opt/willys-pricehunter/app/scanner.py
```
