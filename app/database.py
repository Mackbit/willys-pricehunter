import datetime, pickle, json



class Database():

    def __init__(self, path):
        self.path = path

    def get_week_format(self):
        week_number = datetime.datetime.now().isocalendar()[1]
        year = datetime.datetime.now().year
        s = str(year) + '-W' + str(week_number)
        return s

    def load_data(self, path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
        except:
            data = {}
        return data

    def save_data(self, data, path):
        _data = {'data': data, 'last_update': datetime.datetime.now()}
        with open(path, 'wb') as f:
            pickle.dump(_data, f)

    def bulk_put(self, items):
        wn = self.get_week_format()
        data = self.load_data(self.path)['data']
        for code, item in items.items():
            if data.get(code, None):
                data[code]['price'] = item['price']
                data[code]['name'] = item['name']
                data[code]['comparePrice'] = item['comparePrice']
                data[code]['comparePriceUnit'] = item['comparePriceUnit']
                data[code]['savingsAmount'] = item['savingsAmount']
                data[code]['category'] = item['category']
                data[code]['imageUrl'] = item['imageUrl']
                _item = {'price': item['price'], 'comparePrice': item['comparePrice'],
                         'savingsAmount': item['savingsAmount']}
                data[code]['history'][wn] = _item.copy()
            else:
                data[code] = item.copy()
                data[code]['history'] = {}
                _item = {'price': item['price'], 'comparePrice': item['comparePrice'], 'savingsAmount': item['savingsAmount']}
                data[code]['history'][wn] = _item.copy()
        print('len of data={}'.format(len(data)))
        self.save_data(data, self.path)
