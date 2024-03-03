import time
import os
from bs4 import BeautifulSoup as bs 

import undetected_chromedriver as uc
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import json
import re
import psutil


class OzonParser() : 
    __pages = []
    __links_to_products = []
    __products = []
    __path_to_directory = os.path.abspath(__file__).replace(os.path.basename(__file__),'')
    

    def __parse_pages(self,begining_page,pages_count):
        i = begining_page 
        temp = i
        url = self.url
        if(url.count('?') == 1): 
            url += f'&page={i}'
        else: 
            url += f'/?page={i}'

        while url and i < temp + pages_count:
            print(f'\n\n\n\nСтраница №{i}')

            self.driver.get(url)

            time.sleep(8)

            html_code = bs(self.driver.page_source,'lxml')
            
            self.__pages.append(html_code)
            
            i += 1
            
            #Checking if next page exist
            url_temp = html_code.find('a', {'class' : 'p6e b237-a0 b237-b6 b237-b1'}) 
            if(url_temp != None): 
                url = 'https://www.ozon.ru' + url_temp['href']
            else: 
                url = None


        
    def __parse_links_to_products(self):
        os.system('cls')
        for page in self.__pages:
            divs = page.find_all('div', {'class' : 'xi1'})
            if(divs == []): 
                divs = page.find_all('div', {'class' : 'wi7'})

            for div in divs:
                a = div.find('a', {'class' : 'tile-hover-target it3 ti3'})
                href = a['href']
                self.__parse_product(href.split('?')[0])



    def __parse_product(self,href):
        url = 'https://www.ozon.ru' + href
        product = {}
        
        print({f"\n{url}"})

        memory_percent = psutil.virtual_memory().percent

        if(memory_percent >= 75): 
            self.driver.quit()
            self.driver = uc.Chrome(driver_executable_path=self.driver_path)
            
        try:
            self.driver.get(url = url)
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*")))   
        except TimeoutException:
            self.driver.quit()
            self.driver = uc.Chrome(driver_executable_path=self.driver_path)
            self.driver.get(url = url)
 
        time.sleep(4) 

        html_code = bs(self.driver.page_source,'lxml')
        
        #Checking if the product is not out of stock
        if(html_code.find('h2', {'class' : 'zk4'}) != None): 
            return 
               
        price_temp = self.__parse_price(html_code= html_code)

        product['Название'] = self.__parse_name(html_code= html_code)
        product['Цена со скидкой'] = price_temp[0] #price_with_discount
        product['Цена без скидки'] = price_temp[1] #price_without_discount
        product['Рейтинг'] = self.__parse_rating(html_code= html_code)
        product['Ссылка'] = url
        self.__parse_charasterics(html_code=html_code, product=product)

        
        self.__products.append(product)

    def __parse_price(self,html_code : str):
        price_temp = html_code.find('span', {'class' : 'l6p pl6 ql'})
        if(price_temp is None): 
            price_temp = html_code.find('span', {'class' : 'pl1 pl'})
        if(price_temp is None): 
            price_temp = html_code.find( 'span' ,{'class': 'l6p pl6 l0q'})
        price_with_discount = price_temp.text
    

        price_temp = html_code.find('span', {'class' : 'p5l p6l p4l lp6'})

        if(price_temp is not None): 
            price_without_discount = price_temp.text
        else: price_without_discount = 'Нет'

        return tuple[price_with_discount,price_without_discount]
    
    def __parse_rating(self,html_code: str):
        rating_temp = html_code.find('div', {'class' : 'rv9'})

        if(rating_temp is None): 
            rating_temp = 'Нет' 
        else: 
            rating_temp = rating_temp.find('span').text

        return rating_temp

    def __parse_name(self, html_code: str):   
        temp = html_code.find('h1', {'class' : 'lq1'})
        name_of_product = ''

        if(temp != None): 
            name_of_product = temp.text
        else: 
            name_of_product = 'Не найдено'
        
        return name_of_product

    def __parse_charasterics(self,html_code: str,product):
        name_of_characteristics = html_code.find_all('dt', {'class' : 'j5v'})
        characteristics = html_code.find_all('dd', {'class' : 'vj5'})
        

        for i in range(len(characteristics)):
            name_of_characteristic_temp = name_of_characteristics[i]

            if(name_of_characteristic_temp is None): 
                name_of_characteristic = name_of_characteristics[i].text
            else:
                name_of_characteristic = name_of_characteristic_temp.text  

            if(i < len(name_of_characteristics) - 1 == False): 
                continue
            
            if(name_of_characteristic not in product.keys()):
                product[f'{name_of_characteristic}'] = f'{characteristics[i].text}'          

    

    def __exit(self):
        time.sleep(2)
        self.driver.quit()
        self.driver.service.stop()



    def parse(self,pages_count,begining_page=1):
        self.__parse_pages(begining_page,pages_count)
        self.__parse_links_to_products()
        self.__exit()
        print('Было спарсено: '  + str(len(self.__products)))
        return self.__products
    


    def printProduct(self,index):
        product = self.__products[index]
        keys = product.keys()
        for key in keys:
            print(key + ': ' + product[key])



    def convertToJsonFile(self,file_name='products.json',path=''):
        if(path == ''): path = self.__path_to_directory + file_name
        elif(path != ''): path = path + file_name

        with open(path,'w',encoding='utf-8') as json_file:
            json.dump(self.__products, json_file,indent = 2, ensure_ascii= False)


    
    def __init__(self,url,driver_path = None):
        self.url = url
        self.driver_path = driver_path
        self.driver = uc.Chrome(driver_executable_path=self.driver_path)
