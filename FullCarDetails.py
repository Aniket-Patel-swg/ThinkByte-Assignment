import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv('DB_PASSWORD')

def getCarFullDetails(url):

    conn = psycopg2.connect(
        dbname='ToysData',
        user='postgres',
        password=db_password,
        host='localhost',  
        port='5432'   
    )
    cursor = conn.cursor()

    # Insert data query
    insert_query = '''
        INSERT INTO products (title, link, vendor, regular_price, sale_price, 
        pickup_available_at, pickup_availability, description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''

    create_table_query = """
        CREATE TABLE IF NOT EXISTS full_car_details (
            id SERIAL PRIMARY KEY,
            title TEXT,
            link TEXT,
            vendor TEXT,
            regular_price TEXT,
            sale_price TEXT
        );
    """
    cursor.execute(create_table_query)
    print('created table')

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        product_info = soup.find('product-info')

    # Extracting specific attributes from the custom tag
    if product_info:
        print('getting product info')
        vendor = product_info.find('p', class_='product__text inline-richtext caption-with-letter-spacing')

        title = product_info.find('a', class_='product__title')
        link = title.get('href')

        regularPrice = product_info.find('span', class_='price-item price-item--regular')

        salePrice = product_info.find('span', class_='price-item price-item--sale price-item--last')

        pickUpInfo = product_info.find('pickup-availability-drawer', class_='gradient')
        print('pickUpInfo: ',pickUpInfo)

        # uses shopify's custom tag 
        # if pickUpInfo:
        #     print('getting pickup info')
        #     pickUpAvailableAt = pickUpInfo.find('h3', class_='h4')
        #     print('pickUp: ',pickUpAvailableAt.text)

        #     pickUpAvailablity = pickUpInfo.find('p', class_='pickup-availability-preview caption-large')
        #     print('pickUp: ',pickUpAvailablity.text)

        #     address_tag = soup.find('address', class_='pickup-availability-address')
        #     if address_tag:
        #         print('getting address info')
        #         address = address_tag.get_text('p', strip=True)
        #         print('address: ',address.text)

        product_description_div = soup.find('div', class_='product__description')

        product_description = product_description_div.get_text(separator="\n", strip=True)

        print('product Description: ', product_description)

        cursor.execute(insert_query, (
                title.text.strip(),
                link,
                vendor.text.strip(),
                regularPrice.text.strip(),
                salePrice.text.strip(),
                product_description
            ))

        conn.commit()
        print("Data inserted successfully!")    
    cursor.close()
    conn.close()
getCarFullDetails("https://tinytown.in/products/hot-wheels-donut-drifter-blue")