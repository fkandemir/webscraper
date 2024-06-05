from bs4 import BeautifulSoup
import requests

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