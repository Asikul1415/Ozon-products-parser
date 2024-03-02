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
    pages = []
    links_to_products = []
    products = []
    path_to_directory = os.path.abspath(__file__).replace(os.path.basename(__file__),'')
    
    def parse_pages(self,begining_page,pages_count):
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
            
            self.pages.append(html_code)
            
            i += 1
            
            #Checking if next page exist
            url_temp = html_code.find('a', {'class' : 'p6e b237-a0 b237-b6 b237-b1'}) 
            if(url_temp != None): 
                url = 'https://www.ozon.ru' + url_temp['href']
            else: 
                url = None

        
    def parse_links_to_products(self):
        os.system('cls')
        for page in self.pages:
            divs = page.find_all('div', {'class' : 'xi1'})
            if(divs == []): 
                divs = page.find_all('div', {'class' : 'wi7'})

            for div in divs:
                a = div.find('a', {'class' : 'tile-hover-target it3 ti3'})
                href = a['href']
                self.parse_product(href.split('?')[0])

    def parse_product(self,href):
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
        
        if(html_code.find('h2', {'class' : 'zk4'}) != None): 
            return #Checking if the product is not out of stock
               

        temp = html_code.find('h1', {'class' : 'lq1'})
        name_of_product = ''

        if(temp != None): name_of_product = temp.text
        else: name_of_product = 'Не найдено'


        price_temp = html_code.find('span', {'class' : 'l6p pl6 ql'})
        if(price_temp is None): 
            price_temp = html_code.find('span', {'class' : 'pl1 pl'})
        if(price_temp is None): 
            price_temp = html_code.find( 'span' ,{'class': 'l6p pl6 l0q'})
        price_with_discount = price_temp.text
    

        price_temp = html_code.find('span', {'class' : 'p5l p6l p4l lp6'})
        if(price_temp is not None): price_without_discount = price_temp.text
        else: price_without_discount = 'Нет'


        rating_temp = html_code.find('div', {'class' : 'rv9'})
        if(rating_temp is None): rating_temp = 'Нет' 
        else: rating_temp = rating_temp.find('span').text
        rating = rating_temp



        product['Название'] = name_of_product
        product['Цена со скидкой'] = price_with_discount
        product['Цена без скидки'] = price_without_discount
        product['Рейтинг'] = rating
        product['Ссылка'] = url
        
        
        name_of_characteristics = html_code.find_all('dt', {'class' : 'j5v'})
        characteristics = html_code.find_all('dd', {'class' : 'vj5'})
        

        for i in range(len(characteristics)):
            name_of_characteristic_temp = name_of_characteristics[i]

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

    def parse(self,pages_count,begining_page=1):
        self.parse_pages(begining_page,pages_count)
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
        elif(path != ''): path = path + file_name

        with open(path,'w',encoding='utf-8') as json_file:
            json.dump(self.products, json_file,indent = 2, ensure_ascii= False)
    
    def __init__(self,url,driver_path = None):
        self.url = url
        self.driver_path = driver_path
        self.driver = uc.Chrome(driver_executable_path=self.driver_path)
