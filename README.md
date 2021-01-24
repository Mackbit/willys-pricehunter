# Willys pricehunter

The pricehunter tracks food prices and discounts over time for the Swedish foodstore `Willys`. The project consists of a toy database (a json dict dump) that is created and updated by `scanner.py`. The scanner fetches the latest prices of all Willys products and keeps track of price changes over each new week. All price data is visualized in the fastapi frontend `main.py`. 

See below screenshot examples for 1) dashboard overview and 2) price history details for some 1st class tomatoes.

![Alt text](/images/dashboard.png?raw=true "Dashboard overview")
![Alt text](/images/price_history.png?raw=true "Price history")


## Deploy

Project can easily be deployed on a Ubuntu server by following below steps. 

1. Install docker: `$ apt install docker.io`
2. Clone repo to /opt/
3. `$ mkdir /home/ubuntu/database`
4. Run scanner to initialize database: `$ python3 /opt/willys-pricehunter/app/scanner.py`
5. Run frontend: `$ sh /opt/willys-pricehunter/run.sh`

To get continuous price history, the scanner can be executed once per day by setting a crontab job:

```
0 7 * * * /usr/bin/python3 /opt/willys-pricehunter/app/scanner.py
```

## Possible future improvements

* Convert toy database to a real database such as PostgreSQL
* Make `scanner` a separare micro-service
* Add sign-up user form
* Put user data in database
* Make it possible to add products to a favorite list
* Get email notifications when there is a discount on a product in a tracking list