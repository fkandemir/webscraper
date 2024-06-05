from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time
import os


class Utilization:

    def __init__(self):
        pass

    def createProductFolder(self, folder_name):
        if not os.path.exists("products"):
            os.makedirs("products")
        os.chdir('products')
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        os.chdir(folder_name)
        if not os.path.exists("images"):
            os.makedirs("images")
        os.chdir('images')
        return

    def saveProductInfo(self, product_info):
        os.chdir("..")
        with open("product_info.json", 'w') as json_file:
            json.dump(product_info, json_file, indent=4)
    def downloadImage(self, image_url, save_path):
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)


class WebScraper:
    UTILIZATION_OBJECT = Utilization()

    def __init__(self):
        pass

    ### LAPTOP LINKS AND RATINGS
    def getProductLinks(self):
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

    def getProductDetails(self, links):
        driver = webdriver.Chrome()
        counter = 0
        for link in links:
            product_info = {}
            folder_name = f"laptop_{str(counter + 1)}"
            driver.get(f"https://www.trendyol.com{link}")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comment_section_link = self.getProductCommentLink(soup)
            self.UTILIZATION_OBJECT.createProductFolder(folder_name)
            self.getProductPictures(driver)
            product_info = {
                  "title": self.getProductTitle(soup),
                  "price": self.getProductPrice(soup),
                  "Review Count": self.getProductReviewCount(soup),
                  "Rating Score": self.getProductRatingScore(soup),
                  "Favourites Amount": self.getProductFavAmount(soup),
                  "Seller Name": self.getProductSellerName(soup),
                  "Comments Amount": self.getProductCommentAmount(soup),
                  "Questions Amount": self.getProductQuestionAmount(soup),
                  "Ratings Distribution": self.getProductRatings(driver),
                  "Comments": self.getComments(driver, comment_section_link)
    }
            self.UTILIZATION_OBJECT.saveProductInfo(product_info)
            for i in range(2):
                os.chdir('..')
            counter += 1
            #if counter == 1: break
        driver.quit()
        return


    def getProductTitle(self, soup):
        title = soup.find('h1', class_="pr-new-br")
        product_title = title.find('span').text
        return product_title

    def getProductPrice(self, soup):
        description = soup.find('div', class_="product-price-container")
        price = description.find('span', class_="prc-dsc").text
        return price

    def getProductCommentLink(self, soup):
        div = soup.find('div', class_="rvw-cnt")
        link = div.find('a', href=True)
        return link['href']

    def getProductReviewCount(self, soup):
        review_count = soup.find('span', class_="total-review-count").text
        return review_count

    def getProductRatingScore(self, soup):
        rating = soup.find('div', class_="rating-line-count").text
        return rating

    def getProductFavAmount(self, soup):
        fav_amount = soup.find('span', class_="favorite-count").text
        return fav_amount

    def getProductSellerName(self, soup):
        seller_name = soup.find('a', class_="seller-name-text").text
        return seller_name

    def getProductCommentAmount(self, soup):
        comment_amount = soup.find('p', class_="p-reviews-comment-count").text[:-6]
        return comment_amount

    def getProductQuestionAmount(self, soup):
        question_amount = soup.find('span', class_="question-tag__count").text[1:-1]
        return question_amount

    def getProductRatings(self, driver):
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

    def getProductPictures(self, driver):
        divs = driver.find_elements(By.CLASS_NAME, 'product-slide')
        image_urls = []
        for div in divs:
            if "product-slide video-player" in div.get_attribute('class'):
                continue
            img = div.find_element(By.TAG_NAME, 'img')
            image_urls.append(img.get_attribute('src'))

        for index, url in enumerate(image_urls):
            self.UTILIZATION_OBJECT.downloadImage(url, f'product_image_{index}.jpg')



    ### COMMENT FILTERS
    def getComments(self, driver, link):
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
                comments_array.append([comment_content, int(thumps_up_amount)])
                self.getCommentImages(comment, index, star)
                if counter >= 100:
                    break
            comments_array.append(counter)
        return comments_array

    def getCommentImages(self, comment, index, star):
        comment_photos = comment.find('div', class_='comment-photos')
        if comment_photos:
            review_images = comment_photos.find_all('div', class_='item review-image')
            for image_index, review_image in enumerate(review_images):
                image_url = review_image.get('style', '')[23:-3]
                image_filename = f"{star}star_comment_{index + 1}_image_{image_index + 1}.jpg"
                self.UTILIZATION_OBJECT.downloadImage(image_url, image_filename)

    def initiateScraping(self):
        LINKS = self.getProductLinks()
        self.getProductDetails(LINKS)

if __name__ == '__main__':
    web_scraper = WebScraper()
    web_scraper.initiateScraping()






