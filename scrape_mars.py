# Dependencies
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from pprint import pprint
from flask import render_template
import requests
import pymongo
import pandas as pd
import time

def scrape():
    #dict to store info in
    info_dict = {'news_title': "", 
                'news_paragraph': "",
                'featured_image_url': "", 
                'latest_tweet': "", 
                'mars_table': "", 
                'image_dict_list': ""
                }

    #----------------------------------------------------------------------------------------
    # LATEST MARS NEWS
    #----------------------------------------------------------------------------------------
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')
    # Extract the title of the HTML document
    title = soup.title.text
    # Extract the paragraph of the HTML document
    paragraph = soup.find('p').text

    info_dict['news_title']=title
    info_dict['news_paragraph']=paragraph

    #----------------------------------------------------------------------------------------
    # FEATURED MARS IMAGE
    #----------------------------------------------------------------------------------------
    #click on the full image button using selenium
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    driver = webdriver.Chrome()
    driver.get(url)
    python_button = driver.find_element_by_id('full_image')
    python_button.click()
    #let program catch up to page change
    time.sleep(5)
    #click on the more info button
    python_button = driver.find_element_by_partial_link_text('more info').click()
    #grab the appropr
    soup_level2=bs(driver.page_source, 'lxml')
    url_end = soup_level2.find('img', {'class' : 'main_image' })['src']
    featured_image_url="https://www.jpl.nasa.gov" + url_end

    info_dict['featured_image_url']=featured_image_url

    #----------------------------------------------------------------------------------------
    # CURRENT WEATHER ON MARS
    #----------------------------------------------------------------------------------------
    # Set URL and driver
    url = "https://twitter.com/marswxreport?lang=en"
    driver.get(url)
    # Scrape page into soup
    soup_level1=bs(driver.page_source, 'lxml')
    #latest tweet
    latest_tweet = soup_level1.find('p',{'class' : 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text'}).text

    info_dict['latest_tweet']=latest_tweet

    #----------------------------------------------------------------------------------------
    # MARS FACTS
    #----------------------------------------------------------------------------------------
    #Set URL and scrape the first table using pandas
    url = 'https://space-facts.com/mars/'
    table = pd.read_html(url)[0]
    table.columns = ['Description', 'Value']

    #Export table to html document
    table.to_html('table.html')

    #Create something that I can convert to html
    table_dict = {}
    for i in range(len(table.columns)):
        table_dict[f"ch{i}"] = table.columns.values[i]
        for j in range(len(table)):
            if(i==0):
                table_dict[f"rh{j}"] = table.values[j][i]
            else:
                table_dict[f"rd{j}"] = table.values[j][i]
    info_dict['mars_table']=table_dict

    #----------------------------------------------------------------------------------------
    # MARS HEMISPHERES
    #----------------------------------------------------------------------------------------
    # Set URL and driver
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    driver.get(url)
    # Scrape page into soup
    soup=bs(driver.page_source, 'lxml')

    # save all item tags
    results = soup.find_all('div', class_='item')
    image_dict_list = []

    # Loop through returned results
    for result in results:
        # Error handling
        try:
            dict_item = {'title': "", 'img_url': ""}
            
            #store header
            dict_item['title']=result.find('h3').text
            h3=result.find('h3').text
            
            #click on result
            driver.find_element_by_link_text(h3).click()
            
            #save image url string for the full resolution hemipshere image
            soup_level1=bs(driver.page_source, 'lxml')
            x = soup_level1.find('img', {'class' : 'wide-image'})
            url_end = x["src"]
            image_url="https://astrogeology.usgs.gov" + url_end
            dict_item['img_url']=image_url
            
            #append dict to list
            image_dict_list.append(dict_item)
            
            #go back
            driver.execute_script("window.history.go(-1)")
            
        except Exception as e:
            print(e)

    info_dict['image_dict_list']=image_dict_list

    return info_dict

#print(scrape())