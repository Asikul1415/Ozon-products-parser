# Ozon-products-parser
A parser that parses products and their characteristics from the catalog you need on the website https://www.ozon.ru. Output to JSON file.

Example of cod how to use this parser:

from Parser import OzonParser

parser = OzonParser(url = "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/")

parser.parse(pages_count=1)

parser.convertToJsonFile(file_name="test.json")

As final result we would have a json file which would like this:

![image](https://github.com/Asikul1415/Ozon-products-parser/assets/83174848/67664e03-cd05-4557-badf-0b6d41655dd5)


