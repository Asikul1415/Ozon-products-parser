import time
import os
from bs4 import BeautifulSoup as bs 
import undetected_chromedriver as uc
import json


class OzonParser() :
    driver = uc.Chrome()
    pages = []
    links_to_products = []
    products = []
    path_to_directory = os.path.abspath(__file__).replace(os.path.basename(__file__),'')
    
    def parse_pages(self,pages_count):
        i = 1
        url = self.url
        if(url.count('?') == 1): url.join(f'&page={i}')
        else: url.join(f'/?page={i}')

        while url and i <= pages_count:
            print(f'\n\n\n\nСтраница №{i}')

            self.driver.get(url)

            time.sleep(8)

            html_code = bs(self.driver.page_source,'lxml')
            
            self.pages.append(html_code)
            
            i += 1
            url_temp = html_code.find('a', {'class' : 'ep6 b235-a0 b235-b6 b235-b1'})
            if(url_temp != None): url = 'https://www.ozon.ru' + url_temp['href']
            else: url = None

        
    def parse_links_to_products(self):
        os.system('cls')
        for page in self.pages:
            divs = page.find_all('div', {'class' : 'ix0'})
            for div in divs:
                a = div.find('a', {'class' : 'tile-hover-target it2 ti2'})
                href = a['href']
                self.parse_product(href.split('?')[0])

    def parse_product(self,href):
        url = 'https://www.ozon.ru' + href
        self.driver.get(url = url)

        time.sleep(4)

        html_code = bs(self.driver.page_source,'lxml')
        product = {}
        print(html_code)

        temp = html_code.find('h1', {'class' : 'pl9'})
        name_of_product = ''

        if(temp != None): name_of_product = temp.text
        else: name_of_product = 'Не найдено'

        price_temp = html_code.find('span', {'class' : 'l4p pl4 l8p'})
        if(price_temp is None): price_temp = html_code.find('span', {'class' : 'l4p pl4 p8l'})
        if(price_temp is None): price_temp = html_code.find( 'span' ,{'class ': 'lp l8o'})
        price_with_discount = price_temp.text

        price_temp = html_code.find('span', {'class' : 'p3l p4l p2l lp4'})
        if(price_temp is not None): price_without_discount = price_temp.text
        else: price_without_discount = 'Нет'

        rating_temp = html_code.find('div', {'class' : 'vr6'})
        if(rating_temp is None): rating_temp = 'Нет' 
        else: rating_temp = rating_temp.find('span').text
        rating = rating_temp

        product['Название'] = name_of_product
        product['Цена со скидкой'] = price_with_discount
        product['Цена без скидки'] = price_without_discount
        product['Рейтинг'] = rating
        product['Ссылка'] = url
        
        name_of_characteristics = html_code.find_all('dt', {'class' : 'j3v'})
        characteristics = html_code.find_all('dd', {'class' : 'vj3'})
        

        for i in range(len(characteristics)):
            name_of_characteristic_temp = name_of_characteristics[i].find('span', {'class' : 'v3j'})

            if(name_of_characteristic_temp is None): 
                name_of_characteristic = name_of_characteristics[i].text
            else:
                name_of_characteristic = name_of_characteristic_temp.text  

            if(i < len(name_of_characteristics) - 1 == False): continue
            
            if(name_of_characteristic not in product.keys()):
                product[f'{name_of_characteristic}'] = f'{characteristics[i].text}'          

        self.products.append(product)

    def close_windows(self):
        current_window = self.driver.current_window_handle
        for handle in self.driver.window_handles:
            self.driver.switch_to(handle)
            if(handle != current_window):
                self.driver.close()
    
    def exit(self):
        time.sleep(2)
        self.driver.quit()
        self.driver.service.stop()

    def parse(self,pages_count):
        self.parse_pages(pages_count)
        self.parse_links_to_products()
        self.exit()
        print('Было спарсено: '  + str(len(self.products)))
        return self.products

    def printProduct(self,index):
        product = self.products[index]
        keys = product.keys()
        for key in keys:
            print(key + ': ' + product[key])
    
    def convertToJsonFile(self,file_name='products.json',path=''):
        if(path == ''): path = self.path_to_directory + file_name

        with open(path,'w',encoding='utf-8') as json_file:
            json.dump(self.products, json_file,indent = 2, ensure_ascii= False)
    
    def __init__(self,url):
        self.url = url



