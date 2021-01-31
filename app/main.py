import json, datetime, hashlib, os
import urllib.parse
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, Query, Depends, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import Database
from graphs import create_multiline_plot
from operator import itemgetter
from pydantic import BaseModel


db = Database(os.getenv('DATABASE_PATH'))

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/img", StaticFiles(directory="img"), name="img")
app.mount("/static", StaticFiles(directory="static"), name="static")

USERS = {'21232f297a57a5a743894a0e4a801fc3': 'af727dd94295bb3383a74184fdf74bb3'}


@app.get('/')
async def home(user_id: Optional[str] = Cookie(None)):
    if user_id:
        return RedirectResponse(url=app.url_path_for("dashboard"))
    else:
        return RedirectResponse(url=app.url_path_for("login"))


@app.get('/login')
async def login(request: Request):
    context = {}
    return templates.TemplateResponse("login.html", {"request": request, 'context': context})


def hash(password: str) -> str:
    return hashlib.md5(password.encode('utf8')).hexdigest()


@app.post('/login')
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    context = {}
    _username = hash(username)
    _password = hash(password)
    success = False
    try:
        __password = USERS[_username]
        if _password == __password:
            success = True
    except:
        pass
    if success:
        response = RedirectResponse(url=app.url_path_for("dashboard"), status_code=302)
        response.set_cookie(key="user_id", value=_username, httponly=True, max_age=1800, expires=1800)
        print('User {} {} logged in.'.format(username, _username))
        return response
    else:
        context['error'] = 'Wrong username or password provided.'
        print('Wrong credentials provided for user {}'.format(username))
        return templates.TemplateResponse("login.html", {"request": request, 'context': context})


@app.get('/logout')
async def logout():
    response = RedirectResponse(url=app.url_path_for("login"))
    response.delete_cookie('user_id')
    return response


@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request, filtering: str = None, user_id: Optional[str] = Cookie(None)):
    if not user_id:
        return RedirectResponse(url=app.url_path_for("login"))
    last_update = str(db.load_data(db.path)['last_update']).split('.')[0]
    if not filtering:
        filtering = 'dashboard'
    context = {'this_week': db.get_week_format().replace('-', ' - ').replace('W', 'week '), 'last_update': last_update,
               'filtering': filtering}
    return templates.TemplateResponse("dashboard.html", {"request": request, 'context': context})


def weekday_to_day(date):
    date = str(datetime.datetime.strptime(date + '-1', "%Y-W%W-%w")).split(' ')[0]
    return date

def get_history_amount_savings(data):
    count = 0
    for key, val in data.items():
        if val['savingsAmount'] > 0:
            count += 1
    return count


def get_history_price_fluctuations(data):
    count = 0
    previous = None
    for key, val in data.items():
        current_price = str(round(val['price'] - val['savingsAmount'], 2))
        if previous:
            if not previous == current_price:
                count += 1
        previous = current_price
    return count


@app.get('/favorite/{action}/{code}')
async def favorite(request: Request, action: str, code: str, user_id: Optional[str] = Cookie(None)):
    if not user_id:
        return RedirectResponse(url=app.url_path_for("login"))
    code = code.replace('---', '_')
    _db = db.load_data(db.path)
    try:
        favorites = _db['users'][user_id]
    except:
        favorites = set()
    if action == 'add':
        favorites |= set([code])
    else:
        favorites.remove(code)
    db.favorites_put(user_id, favorites)
    url = '/product/{}'.format(code.replace('_', '---'))
    response = RedirectResponse(url=url)
    return response


@app.get('/product/{code}', response_class=HTMLResponse)
async def product(request: Request, code: str, user_id: Optional[str] = Cookie(None)):
    if not user_id:
        return RedirectResponse(url=app.url_path_for("login"))
    _db = db.load_data(db.path)
    data = _db['data']
    code = code.replace('---', '_')
    values = data[code]

    favorite = False
    try:
        if code in _db['users'][user_id]:
            favorite = True
    except:
        pass

    dates = []
    prices = []
    actual_prices = []
    savings = []
    for date, value in values['history'].items():
        dates.append(weekday_to_day(date))
        price = value['price']
        saving = value['savingsAmount']
        savings.append(saving)
        prices.append(price)
        actual_prices.append(price-saving)
    values['maxPrice'] = round(max(prices), 2)
    values['minPrice'] = round(min(actual_prices), 2)
    values['currentPrice'] = round(values['price'] - values['savingsAmount'], 2)
    values['savingsCount'] = get_history_amount_savings(values['history'])
    savingspercent = round((1 - (values['price'] - values['savingsAmount']) / values['price']) * 100.0, 2)
    values['savingsPercent'] = savingspercent
    values['savingsAmount'] = round(values['savingsAmount'], 2)
    values['favorite'] = favorite
    values['code'] = code

    today = str(datetime.datetime.now()).split(' ')[0]
    if not today == dates[-1]:
        dates.append(today)
        actual_prices.append(actual_prices[-1])
        savings.append(savings[-1])

    bar0 = create_multiline_plot(dates, [actual_prices, savings],
                                 ['Actual price', 'Saving'],
                                 ['rgba(212, 134, 0, 0.2)', 'rgba(0, 160, 51, 0.2)'],
                                 ['rgba(212, 134, 0, 0.99)', 'rgba(0, 160, 51, 0.99)'])
    layout0 = json.dumps({'title': 'Price history',
                          'legend': {'orientation': 'h', 'x': 0.0, 'y': 1.05},
                          'margin': {'r': 35},
                          'dragmode': False,
                          'xaxis': {'ticklen': 10, 'fixedrange': True},
                          'yaxis': {'automargin': True, 'ticklen': 10, 'ticksuffix': ' SEK', 'fixedrange': True}})

    return templates.TemplateResponse("product.html", {"request": request, 'context': values, 'plot':bar0, 'layout': layout0})




@app.get('/paginating/{filtering}')
async def paginating(request: Request, filtering: str, draw: int, start: int, length: int):
    headers = ['name', 'price', 'currentPrice', 'savingsAmount', 'savingsPercent', 'savingCnt', 'availableCnt', 'flucCnt', 'category']
    qq = str(request.query_params)
    qq = urllib.parse.unquote(qq)
    qqq = qq.split('&')
    _q = {}
    for pair in qqq:
        a, b = pair.split('=')
        _q[a] = b
    search = _q['search[value]'].lower()
    sort_index = int(_q['order[0][column]'])
    _order = _q['order[0][dir]']
    rows, datalen, datasorted = _paginate(start, length, headers[sort_index], _order, search, headers, filtering)
    resp = {"draw": draw, "recordsTotal":datalen,"recordsFiltered":datasorted, "data": rows}
    return resp


def _paginate(offset, limit, sort, order, search, headers, filtering):
    data = db.load_data(db.path)['data']
    data_len = len(data)
    _data = []
    for code, block in data.items():
        dd = block.copy()
        name = dd['name']
        dd['category'] = block['category'].split('/')[0]
        if search:
            if not search in name.lower() and not search in dd['category']:
                continue
        url = '<a href="/product/{}">{}</a>'.format(code.replace('_', '---'), name)
        dd['name'] = url
        if block['savingsAmount'] > 0.0:
            savingspercent = round((1-(block['price'] - block['savingsAmount'])/block['price'])*100.0, 2)
            dd['currentPrice'] = round(block['price'] - block['savingsAmount'], 2)
        else:
            savingspercent = 0
            dd['currentPrice'] = block['price']
        dd['savingsPercent'] = savingspercent
        dd['savingsAmount'] = round(dd['savingsAmount'], 2)
        dd['savingCnt'] = get_history_amount_savings(block['history'])
        dd['availableCnt'] = len(block['history'])
        dd['flucCnt'] = get_history_price_fluctuations(block['history'])
        _data.append(dd)
    if sort:
        if order == 'asc':
            _data = sorted(_data, key=itemgetter(sort), reverse=False)
        else:
            _data = sorted(_data, key=itemgetter(sort), reverse=True)
    output = _data[offset:offset+limit]
    rows = []
    for out in output:
        row = [str(out[s]) for s in headers]
        rows.append(row)
    return rows, data_len, len(_data)