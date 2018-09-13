#!/usr/bin/python

from selenium import webdriver
from functools import reduce


def get_product_attribute_elements(url):
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get('http://google.com')




    driver.close()


if __name__ == '__main__':
    get_product_attribute_elements('https://us.boohoo.com/high-shine-v-hem-bandeau/DZZ09839.html')
