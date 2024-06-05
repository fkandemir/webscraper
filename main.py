from bs4 import BeautifulSoup
import requests
import time
from selenium.webdriver import ActionChains

def getProductLinks():
    laptop_links = []
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
    return laptop_links

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