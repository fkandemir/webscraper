from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os

counter = 0


def createProductFolder(folder_name):
    os.chdir('products')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    os.chdir(folder_name)
    if not os.path.exists("images"):
        os.makedirs("images")
    os.chdir('images')
    return


def saveProductInfo(product_info, folder_name):
    os.chdir("..")
    with open("product_info.json", 'w') as json_file:
        json.dump(product_info, json_file, indent=4)



### LAPTOP LINKS AND RATINGS
def getProductLinks():
    laptop_links = []
    laptop_rating_amounts = []
    pi = 1
    condition = True
    while condition:
        link = f"https://www.trendyol.com/laptop-x-c103108?sst=MOST_RATED&pi={pi}"
        html_data = requests.get(link)
        soup = BeautifulSoup(html_data.content, 'html.parser')
        laptop_cards = soup.find_all('div', class_='p-card-wrppr with-campaign-view')
        pi += 1
        for laptop in laptop_cards:
            ratingCount = laptop.find('span', class_='ratingCount')
            if int(ratingCount.text[1:-1]) >= 300:
                laptop_links.append(laptop.find('a').get('href'))
                #laptop_rating_amounts.append(int(ratingCount.text[1:-1]))
            else:
                condition = False
                break
    return laptop_links#, laptop_rating_amounts

def getProductDetails(links):
    driver = webdriver.Chrome()
    comment_section_links = []
    counter = 0
    for link in links:
        product_info = {}
        folder_name = f"laptop_{str(counter + 1)}"
        driver.get(f"https://www.trendyol.com{link}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #print(f"Title: {getProductTitles(soup)}")
        #comment_section_links.append(getProductCommentLink(soup))
        comment_section_link = getProductCommentLink(soup)
        #print(f"Price: {getProductPrice(soup)}")
        #print(f"Review Count: {getProductReviewCount(soup)}")
        #print(f"Rating Score: {getProductRatingScore(soup)}")
        #print(f"Favourites Amount: {getProductFavAmount(soup)}")
        #print(f"Seller Name: {getProductSellerName(soup)}")
        #print(f"Comments Amount: {getProductCommentAmount(soup)}")
        #print(f"Questions Amount: {getProductQuestionAmount(soup)}")
        #print(f"Ratings Distribution: {getProductRatings(driver)}")
        #one_star_comments, five_star_comments = getOneStarComments(driver, comment_section_link)
        createProductFolder(folder_name)
        getProductPictures(driver, folder_name)
        product_info = {
              "title": getProductTitle(soup),
              "price": getProductPrice(soup),
              "Review Count": getProductReviewCount(soup),
              "Rating Score": getProductRatingScore(soup),
              "Favourites Amount": getProductFavAmount(soup),
              "Seller Name": getProductSellerName(soup),
              "Comments Amount": getProductCommentAmount(soup),
              "Questions Amount": getProductQuestionAmount(soup),
              "Ratings Distribution": getProductRatings(driver),
              "Comments": getComments(driver, comment_section_link)
              #"Five Star Comments": five_star_comments
}
        saveProductInfo(product_info, folder_name)
        for i in range(2):
            os.chdir('..')
        counter += 1
        if counter == 2: break
    #print(comment_section_links)
    driver.quit()
    return #comment_section_links


def getProductTitle(soup):
    title = soup.find('h1', class_="pr-new-br")
    product_title = title.find('span').text
    return product_title

def getProductPrice(soup):
    description = soup.find('div', class_="product-price-container")
    price = description.find('span', class_="prc-dsc").text
    return price

def getProductCommentLink(soup):
    div = soup.find('div', class_="rvw-cnt")
    link = div.find('a', href=True)
    return link['href']

def getProductReviewCount(soup):
    review_count = soup.find('span', class_="total-review-count").text
    return review_count

def getProductRatingScore(soup):
    rating = soup.find('div', class_="rating-line-count").text
    return rating

def getProductFavAmount(soup):
    fav_amount = soup.find('span', class_="favorite-count").text
    return fav_amount

def getProductSellerName(soup):
    seller_name = soup.find('a', class_="seller-name-text").text
    return seller_name

def getProductCommentAmount(soup):
    comment_amount = soup.find('p', class_="p-reviews-comment-count").text[:-6]
    return comment_amount

def getProductQuestionAmount(soup):
    question_amount = soup.find('span', class_="question-tag__count").text[1:-1]
    return question_amount

def getProductRatings(driver):
    star_amounts = []
    element_to_hover_over = driver.find_element(By.CLASS_NAME, 'review-tooltip')
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tooltip_content = soup.find('div', class_='review-tooltip-content')
    star_amounts_div = tooltip_content.find_all('div', class_="pr-rnr-st-c")
    for amount in star_amounts_div:
        star_amounts.append(amount.text)

    return star_amounts


def downloadImage(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)


def getProductPictures(driver, folder_name):
    divs = driver.find_elements(By.CLASS_NAME, 'product-slide')
    image_urls = []
    for div in divs:
        if "product-slide video-player" in div.get_attribute('class'):
            continue
        img = div.find_element(By.TAG_NAME, 'img')
        image_urls.append(img.get_attribute('src'))

    for index, url in enumerate(image_urls):
        downloadImage(url, f'product_image_{index}.jpg')



### COMMENT FILTERS
def getComments(driver, link):
    comments_array = []
    for i in [4,0]:
        counter = 0
        driver.get(f"https://www.trendyol.com{link}")
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.1);")
        time.sleep(2)
        divs = driver.find_elements(By.CLASS_NAME, 'ps-stars__content')

        divs[i].click()
        if i == 4: star = 1
        else: star = 5
        time.sleep(2)
        for i in range(3):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.99);")
            time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        comments = soup.find_all('div', class_="comment")
        time.sleep(3)
        for index, comment in enumerate(comments):
            counter += 1
            comment_content = comment.find('div', class_='comment-text').text
            thumps_up_amount = comment.find('div', class_="rnr-com-like").text[1:-1]
            comments_array.append(comment_content)
            getCommentImages(comment, index, star)
            #extract_and_download_images(driver)
            if counter >= 100:
                break
        comments_array.append(counter)
    return comments_array


def getCommentImages(comment, index, star):
    comment_photos = comment.find('div', class_='comment-photos')
    if comment_photos:
        review_images = comment_photos.find_all('div', class_='item review-image')
        for image_index, review_image in enumerate(review_images):
            image_url = review_image.get('style', '')[23:-3]
            image_filename = f"{star}star_comment_{index + 1}_image_{image_index + 1}.jpg"
            downloadImage(image_url, image_filename)
            #print(image_url)

LINKS = getProductLinks()
getProductDetails(LINKS)





