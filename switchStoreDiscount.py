import os
import re

import eel
from jinja2 import Environment, FileSystemLoader
from pyquery import PyQuery as pq

root = os.path.dirname(os.path.abspath(__file__))

templates_dir = os.path.join(root, "web/")
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('base.html')
filename = os.path.join(templates_dir, 'index.html')

baseURL = 'https://eshop-prices.com'
subURL = '/games/on-sale?currency=CNY'
gamelist = []
eel.init('web/')


def findURL(urltext):
    filter = 'cdn01.*?jpg'
    filter2 = 'https%3A.*?jpg'
    try:
        url = 'http://' + re.search(filter, urltext).group().replace('%2F', '/')
    except AttributeError:
        try:
            url = re.search(filter2, urltext).group().replace('%2F', '/').replace('%3A', ':')
        except AttributeError:
            return None
    return url


def getGameList(baseURL, subURL):
    targetURL = baseURL + subURL
    print(targetURL)
    page = pq(url=(baseURL + subURL))
    all_div = page('div.games-list-item-content')
    japan_us_div = all_div(
        'img[title=Japan], img[title="United States"]').parents('a.games-list-item').items()
    for tab in japan_us_div:
        pictureURL = findURL(tab('picture img').attr('src'))
        tab('.games-list-item-image').remove()
        gamename = tab('h5').text()
        gameorigin = float(tab('del').text().replace('¥', '0'))
        gameprice = float(tab('span.price-tag').remove('del').text().replace('¥', '0'))
        gamediscount = format(gameprice / gameorigin, '.0%')
        store = tab('img').attr('title')
        game = {
            'name': gamename,
            'picture': pictureURL,
            'price': '¥' + str(gameprice),
            'discount': gamediscount,
            'store': store
        }
        gamelist.append(game)
    nextURL = page('span.next a').attr('href')
    if nextURL:
        return getGameList(baseURL, nextURL)
    else:
        return gamelist


if __name__ == '__main__':
    getGameList(baseURL, subURL)
    with open(filename, 'w', encoding='UTF-8') as fh:
        output = template.render(gamelist=gamelist)
        fh.write(output)
    eel.start('index.html', size=(900, 800))
