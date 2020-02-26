import json
import requests
from bs4 import BeautifulSoup as bs

# DesignerList4__designerName DesignerList4__designerName--productsAvailable
with open("data.json", "r") as read_file:
    data = json.load(read_file)
    designers = data["designerNames"]
    userAgent = data["user-agent"]

headers = {'accept': '*/*',
           'user-agent': f'{userAgent}'}

base_url = 'https://www.mrporter.com/en-ru/mens/azdesigners'

def intersection(arr1,arr2):
    array = []
    for element in arr1:
        if element in arr2:
            array.append(element)
    return array


def parse_DesignersList_URL(base_url, headers, myDesignersList):
    session = requests.session()
    request = session.get(base_url, headers=headers)
    soup = bs(request.content, 'lxml')

    designer_URL = dict()
    available_DesignerNames = soup.find_all('a', attrs={'class': 'DesignerList4__designerName DesignerList4__designerName--productsAvailable'})
    availableDesigners_fromList = []

    for d in available_DesignerNames:
        designerName = d.find('meta')['content']
        href = d['href']
        designer_URL[designerName] = f'https://www.mrporter.com{href}'

    for d in designer_URL:
        if d in myDesignersList:
            availableDesigners_fromList.append(d)

    DesignersWeLookFor = dict()
    for aD in availableDesigners_fromList:
        if aD in designer_URL:
            DesignersWeLookFor[aD] = designer_URL[aD]
    return DesignersWeLookFor

BrandsDict = parse_DesignersList_URL(base_url, headers, designers)

def openBrandPage(brandsDictURLs, headers):
    session = requests.session()
    for urls in brandsDictURLs.items():
        url = urls[1]
        request = session.get(url, headers=headers)
        soup = bs(request.content, 'lxml')
        items = soup.find_all('div', attrs={'itemprop':'item'})
        for item in items:
            print(item)

openBrandPage(BrandsDict, headers)


