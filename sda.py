from Parser import OzonParser

#Пример запроса
#Example request

parser = OzonParser(url = "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/")

parser.parse(pages_count=1)

parser.convertToJsonFile(file_name="test.json")


