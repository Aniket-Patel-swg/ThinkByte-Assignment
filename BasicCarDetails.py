import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv('DB_PASSWORD')

def getCarDetails(baseUrl,pageNumber):

    conn = psycopg2.connect(
        dbname='ToysData',
        user='postgres',
        password=db_password,
        host='localhost',  
        port='5432'   
    )
    cursor = conn.cursor()

    insert_query = '''
        INSERT INTO cars (title, link, vendor, regular_price, sale_price) 
        VALUES (%s, %s, %s, %s, %s)
    '''
        
    for i in range(1,pageNumber+1):
        url = f'{baseUrl}/collections/all?page={i}'
        print('getting data for: ', url)   
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            carDetails = soup.find_all('div', class_='card__information')

            finalData = {}
            test = 0
            for cars in carDetails:
                if (cars.find('div', class_='card-information')):
                    titles = cars.find('a', class_='full-unstyled-link')
                    links = titles.get('href')
                    test = test + 1
                    print('test',test)
                    # print('titles: ',titles.text, 'links: ',links)

                    vendor = cars.find('div', class_ ='caption-with-letter-spacing light')
                    # print('vendor: ',vendor.text)

                    regularPrice = cars.find('span', class_='price-item price-item--regular')
                    # print('regularPrice: ',regularPrice.text)

                    salePrice = cars.find('span', class_='price-item price-item--sale price-item--last')
                    # print('salePrice: ',salePrice.text)

                    # finalData[f'Car: {titles.text.strip()}'] = {
                    #     'titles': titles.text.strip(),
                    #     'links': links,
                    #     'vendor': vendor.text.strip(),
                    #     'regularPrice': regularPrice.text.strip(),
                    #     'salePrice': salePrice.text.strip()
                    # }
                    # # print(finalData)
                    # file = open(f'carDetails{i}', 'a')
                    # file.write(str(finalData))

                    title_text = titles.text.strip()
                    link_text = links
                    vendor_text = vendor.text.strip() 
                    regular_price_text = regularPrice.text.strip()
                    sale_price_text = salePrice.text.strip()
                    cursor.execute(insert_query, (title_text, link_text, vendor_text, regular_price_text, sale_price_text))

            conn.commit()
    cursor.close()
    conn.close()
base_url = 'https://www.tinytown.in'

# getting total number pages 
response = requests.get(base_url+'/collections/all?page=1')

soup = BeautifulSoup(response.text, 'html.parser')

pagination = soup.find_all('a', class_='pagination__item')
maxPage = 0
for page in pagination:
    print(type(page.text))
    if page.text.strip().isdigit():
        
        pageNumber = int(page.text)
        if (pageNumber > maxPage):
            maxPage = pageNumber
print('maxPage: ',maxPage)

getCarDetails(base_url+'/collections/all?page=1',maxPage)