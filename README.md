# Willys pricehunter

The Willys pricehunter project consists of a toy database (a json dump) that is created and updated by `scanner.py` that fetches the latest prices of all Willys products. The data is visualized in a fastapi frontend. 

# Deploy

1. Clone repo to /opt/
2. `$ mkdir /home/ubuntu/database`
3. Run scanner to initialize database: `$ python3 /opt/willys-pricehunter/app/scanner.py`
4. Run frontend: `$ sh /opt/willys-pricehunter/run.sh`

The scanner can be executed once per day by setting a crontab job:

```
0 7 * * * /usr/bin/python3 /opt/willys-pricehunter/app/scanner.py
```
