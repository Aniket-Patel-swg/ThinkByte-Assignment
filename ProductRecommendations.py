import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv('DB_PASSWORD')

def getProductRecommendations(url):

    conn = psycopg2.connect(
        dbname='ToysData',
        user='postgres',
        password=db_password,
        host='localhost',  
        port='5432'   
    )
    cursor = conn.cursor()

    # copied from browser network tab if required
    # headers = {
    #     'accept': '*/*',
    #     'accept-encoding': 'gzip, deflate, br, zstd',
    #     'accept-language': 'en-US,en;q=0.9',
    #     'cookie': 'secure_customer_sig=; localization=IN; _tracking_consent=%7B%22con%22%3A%7B%22CMP%22%3A%7B%22a%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A%22%22%2C%22s%22%3A%22%22%7D%7D%2C%22v%22%3A%222.1%22%2C%22region%22%3A%22INGJ%22%2C%22reg%22%3A%22%22%7D; _cmp_a=%7B%22purposes%22%3A%7B%22a%22%3Atrue%2C%22p%22%3Atrue%2C%22m%22%3Atrue%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22sale_of_data_region%22%3Afalse%7D; _shopify_y=9669cd17-2eef-44cb-8826-38c5b1a4c66c; _orig_referrer=https%3A%2F%2Fwww.google.com%2F; _landing_page=%2Fcollections%2Fall; _gid=GA1.2.28196594.1727197034; _gcl_au=1.1.1345644685.1727197036; _fbp=fb.1.1727197035820.852786052527170919; receive-cookie-deprecation=1; _shopify_sa_p=; rzp_magic_landing=https%3A%2F%2Fwww.tinytown.in%2Fproducts%2Fhot-wheels-donut-drifter-blue; qab_previous_pathname=/products/hot-wheels-donut-drifter-blue; _shopify_s=d3753ac8-8e14-43c7-9921-f01e295fbc81; _shopify_sa_t=2024-09-25T10%3A53%3A55.773Z; _ga_QWZW5JM7W0=GS1.1.1727261147.8.1.1727261635.0.0.0; _ga=GA1.1.1491332254.1727197034; _ga_V7RMT0EJY2=GS1.1.1727261149.7.1.1727261635.0.0.0; keep_alive=20d01f2e-3de4-44b4-a4c7-379decbfbf50',
    #     'priority' : 'u=1, i',
    #     'referer': 'https://www.tinytown.in/products/hot-wheels-donut-drifter-blue',
    #     'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    # }

    print('getting recommendations')
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        form = soup.find('form', class_='installment caption-large')
        
        if form:

            product_id = form.find('input', {'name': 'product-id'})['value']
            section_id = form.find('input', {'name': 'section-id'})['value']
            cleaned_section_id = section_id.replace('__main', '')
            limit = 4

            print('Product ID:', product_id)
            print('Section ID:', cleaned_section_id)

            recommendationResponse = requests.get(f'https://www.tinytown.in/recommendations/products?section_id={cleaned_section_id}__related-products&product_id={product_id}&limit={limit}',
                                                 )
            # print('recommendationResponse: ', recommendationResponse)
            print(recommendationResponse.headers.get('Content-Encoding'))

            # print('recommendationResponse: ', recommendationResponse.content)

            if response.status_code == 200:

                recommendationParsedHTML = BeautifulSoup(recommendationResponse.content, 'html.parser')

                with open('recommendationResponse.html', 'wb') as file:
                    file.write(recommendationResponse.content)

                recommendationLists = recommendationParsedHTML.find_all('li', class_='grid__item')
                print('recommendationLists: ', len(recommendationLists))

                for recommendation in recommendationLists:

                    title = recommendation.find('a', class_='full-unstyled-link')
                    print('title: ', title.text)
                    link = title.get('href')
                    print('link: ', link)
                    # price = recommendation.find('span', class_='price-item price-item--regular')
                    # print('price: ', price.text)

                    regularPrice = recommendation.find('span', class_='price-item price-item--regular')
                    print('regularPrice: ', regularPrice.text)

                    salePrice = recommendation.find('span', class_='price-item price-item--sale price-item--last')
                    print('salePrice: ', salePrice.text)

                    cursor.execute("""
                        INSERT INTO product_recommendations (title, link, regular_price, sale_price)
                        VALUES (%s, %s, %s, %s);
                    """, (title, link, regularPrice, salePrice))
            conn.commit()
            print("Data inserted successfully!")
        else:
            print('Form not found.')
            
    cursor.close()
    conn.close()
getProductRecommendations("https://www.tinytown.in/products/maisto-bmw-s1000rr-metallic-green-1-18")
