import json
import requests
from bs4 import BeautifulSoup as bs
import io, base64
import xlsxwriter as xw

wbClothe = xw.Workbook('Clothes.xlsx')
wsClothes = wbClothe.add_worksheet('MrPorter')

with open("data.json", "r") as read_file:
    data = json.load(read_file)
    designers = data["designerNames"]
    userAgent = data["user-agent"]


headers = {'accept': '*/*',
           'user-agent': f'{userAgent}'}
base_url = 'https://www.mrporter.com/en-ru/mens/azdesigners'


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



def showAllURLs(brandsDictURLs, headers):
    session = requests.session()
    avURLs = []

    for urls in brandsDictURLs.items():
        brand = urls[0].replace(' ', '-')
        url = urls[1]
        avURLs.append(url)
        request = session.get(url, headers=headers)

        if request.status_code == 200:
            soup = bs(request.content, 'lxml')

            try:
                pagination = soup.find_all('a', attrs={'class': 'Pagination6__last'})
                for page in pagination:
                    count = int(page['href'].rsplit('=')[1]) + 1
                    for brandPage in range(count):
                        if brandPage == 1 or brandPage == 0:
                            pass
                        else:
                            url = f'https://www.mrporter.com/en-ru/mens/designer/{brand}?pageNumber={brandPage}'
                            if url not in avURLs:
                                avURLs.append((url))
            except:
                pass

    return avURLs
itemsURLs = showAllURLs(BrandsDict, headers)



def checkItems(itemsURLs, headers):
    session = requests.session()
    foundItems = []

    for url in itemsURLs:
        request = session.get(url, headers=headers)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')

            try:
                items = soup.find_all('a')
                for item in items:
                    try:
                        brand = item.find('span', attrs={'data-testid': 'pid-summary-designer'}).text
                        imgDiv = item.find('div', attrs={'class': 'primaryImage'})
                        primaryImageSRC = imgDiv.find('div', attrs={'class': 'Image17__imageContainer'})
                        noScript = item.find('noscript')
                        imageSRC = noScript.find('img')['src']
                        # imageSRC = (primaryImageSRC.find('img'))['src']
                        # imageSRC = (primaryImageSRC.find('img', attrs={'sizes': '(min-width: 768px) 25vw, 50vw'}))['src']
                        image = f'https:{imageSRC}'
                        # image = io.BytesIO(base64.b64decode(imageSRC.split(',')[1]))
                        # image = base64.urlsafe_b64decode(imageSRC + '=' * (4 - len(imageSRC) % 4))
                        # im.save("image.jpg")
                        # image = base64.b64decode(imageSRC)
                        description = item.find('span', attrs={'data-testid': 'pid-summary-description'}).text
                        price = item.find('span', attrs={'itemprop': 'price'}).text
                        link = item['href']

                        foundItems.append({
                            'brand': brand,
                            'image': image,
                            'description': description,
                            'price': price,
                            'link': f'https://www.mrporter.com{link}'
                        })

                    except:
                        pass

            except:
                pass
    return foundItems

foundClothes = checkItems(itemsURLs, headers)
print(foundClothes)
print(len(foundClothes))

row_number = 0
col_number = 0

for item in foundClothes:
    wsClothes.write(row_number, col_number, item['brand'])
    wsClothes.write(row_number, col_number+1, item['image'])
    wsClothes.write(row_number, col_number+2, item['description'])
    wsClothes.write(row_number, col_number+3, item['price'])
    wsClothes.write(row_number, col_number+4, item['link'])

    row_number += 1

wbClothe.close()

