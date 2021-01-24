import requests, json, traceback, time


class Willys:

    def __init__(self):
        self.url = 'https://www.willys.se'


    def fetch_pagination(self, url):
        index = 0
        data = []
        _url = url
        while True:
            print('Fetching URI={}'.format(_url))
            try:
                r = requests.get(_url, timeout=10)
                _data = json.loads(r.text)
            except:
                print('Failing to fetch data, sleeping 5 seconds...')
                time.sleep(5)
                continue
            nop = _data['pagination']['numberOfPages']
            data += _data['results']
            if index == nop-1:
                break
            index += 1
            _url = url + '&page={}'.format(index)
            time.sleep(0.5)
        return data


    def fetch_category(self, category):
        avoid_cache = str(int(time.time()*1000.0))
        size = 50
        url = self.url + '/c/{}?avoidCache={}&categoryPath={}&code=&size={}'.format(category, avoid_cache, category, size)
        data = self.fetch_pagination(url)
        return data

    def parse_data(self, data):
        output = {}
        for category, products in data.items():
            for product in products:
                try:
                    name = product['name']
                    price = float(product['priceValue'])
                    try:
                        comp_price = float(product['comparePrice'].replace(',', '.').replace('kr', '').strip())
                    except:
                        comp_price = product['comparePrice']
                    comp_price_unit = product['comparePriceUnit']
                    saving = product.get('savingsAmount', 0)
                    url = product['image']['url']
                    if not saving:
                        saving = 0
                    saving = float(saving)

                    try:
                        code = product['code']
                    except:
                        print('product {} is missing code, skipping...'.format(name))
                        continue

                    try:
                        manufacturer = product['manufacturer']
                    except:
                        manufacturer = ''
                        print('product {} is missing manufacturer'.format(name))

                    output[code] = {'price': price, 'comparePrice': comp_price, 'comparePriceUnit': comp_price_unit,
                                    'savingsAmount': saving, 'category': category, 'imageUrl': url, 'name': name,
                                    'manufacturer': manufacturer}
                    #print('{}: {} -- {}/{} {}'.format(name, price, comp_price, comp_price_unit, saving))
                except:
                    print('ERROR: Failed to parse product with name={}'.format(product['name']))
                    print(traceback.format_exc())
        return output


    def scan(self, categories):
        data = {}
        for category in categories.keys():
            cname = category.lower()
            data[cname] = self.fetch_category(category)
        data = self.parse_data(data)
        return data

