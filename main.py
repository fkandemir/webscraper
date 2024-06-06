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
        # Create 'products' directory if it does not exist
        if not os.path.exists("products"):
            os.makedirs("products")
        os.chdir('products')  # Change to 'products' directory
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)  # Create product folder if it does not exist
        os.chdir(folder_name)  # Change to product folder
        if not os.path.exists("images"):
            os.makedirs("images")  # Create 'images' folder if it does not exist
        os.chdir('images')  # Change to 'images' folder
        return

    def saveProductInfo(self, product_info):
        os.chdir("..")  # Change to product folder
        with open("product_info.json", 'w') as json_file:
            json.dump(product_info, json_file, indent=4)  # Save product info as JSON

    def downloadImage(self, image_url, save_path):
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)  # Download and save image

    def create_output_jsonl(self):
        os.chdir("products")
        try:
            current_dir = os.getcwd()
            directories = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]

            os.chdir("..")
            output_data = {}
            for directory in directories:
                output_data[directory] = os.path.join("/products", directory, "images")

            with open("output.jsonl", "w") as f:
                for key, value in output_data.items():
                    json_line = json.dumps({key: value})
                    f.write(json_line + "\n")
        except Exception as e:
            print(f"An error occurred while processing directories: {e}")
            return


class WebScraper:
    UTILIZATION_OBJECT = Utilization()

    def __init__(self):
        pass

    def getProductLinks(self):
        laptop_links = []
        pi = 1  # Page index
        condition = True
        while condition:
            link = f"https://www.trendyol.com/laptop-x-c103108?sst=MOST_RATED&pi={pi}"
            html_data = requests.get(link)
            soup = BeautifulSoup(html_data.content, 'html.parser')
            laptop_cards = soup.find_all('div', class_='p-card-wrppr with-campaign-view')
            pi += 1  # Increment page index for next page
            for laptop in laptop_cards:
                ratingCount = laptop.find('span', class_='ratingCount')
                if int(ratingCount.text[1:-1]) >= 100:  # Check if rating count is 100 or more
                    laptop_links.append(laptop.find('a').get('href'))  # Add laptop link
                else:
                    condition = False  # Exit loop if rating count is less than 100
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
                os.chdir('..')  # Navigate back to the root directory
            counter += 1
        driver.quit()
        return

    def getProductTitle(self, soup):
        title = soup.find('h1', class_="pr-new-br")
        product_title = title.find('span').text  # Extract product title
        return product_title

    def getProductPrice(self, soup):
        description = soup.find('div', class_="product-price-container")
        price = description.find('span', class_="prc-dsc").text  # Extract product price
        return price

    def getProductCommentLink(self, soup):
        div = soup.find('div', class_="rvw-cnt")
        link = div.find('a', href=True)
        return link['href']  # Extract comment section link

    def getProductRatingScore(self, soup):
        rating = soup.find('div', class_="rating-line-count").text  # Extract rating score
        return rating

    def getProductFavAmount(self, soup):
        fav_amount = soup.find('span', class_="favorite-count").text  # Extract favourite count
        return fav_amount

    def getProductSellerName(self, soup):
        seller_name = soup.find('a', class_="seller-name-text").text  # Extract seller name
        return seller_name

    def getProductCommentAmount(self, soup):
        comment_amount = soup.find('p', class_="p-reviews-comment-count").text[:-6]  # Extract comment amount
        return comment_amount

    def getProductQuestionAmount(self, soup):
        question_amount = soup.find('span', class_="question-tag__count").text[1:-1]  # Extract question amount
        return question_amount

    def getProductRatings(self, driver):
        star_amounts = []
        element_to_hover_over = driver.find_element(By.CLASS_NAME, 'review-tooltip')
        hover = ActionChains(driver).move_to_element(element_to_hover_over)
        hover.perform()  # Hover over the rating element to display tooltip
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tooltip_content = soup.find('div', class_='review-tooltip-content')
        star_amounts_div = tooltip_content.find_all('div', class_="pr-rnr-st-c")
        for amount in star_amounts_div:
            star_amounts.append(amount.text)  # Extract star ratings
        return star_amounts

    def getProductPictures(self, driver):
        divs = driver.find_elements(By.CLASS_NAME, 'product-slide')
        image_urls = []
        for div in divs:
            if "product-slide video-player" in div.get_attribute('class'):
                continue  # Skip video slides
            img = div.find_element(By.TAG_NAME, 'img')
            image_urls.append(img.get_attribute('src'))  # Collect image URLs
        for index, url in enumerate(image_urls):
            self.UTILIZATION_OBJECT.downloadImage(url, f'product_image_{index}.jpg')  # Download images

    def getComments(self, driver, link):
        comments_array = []
        my_index = 0
        for i in range(2):
            counter = 0
            driver.get(f"https://www.trendyol.com{link}")
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.1);")
            time.sleep(4) # Wait for page to load
            divs = driver.find_elements(By.CLASS_NAME, 'ps-stars__content')
            divs[my_index].click()  # Click on the star rating filter
            if i == 4:
                star = 1
            else:
                star = 5
            time.sleep(2) # Wait for page to load
            for i in range(3):
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.95);") # Scroll down to load more comments
                time.sleep(3)  # Wait for page to load
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comments = soup.find_all('div', class_="comment")
            time.sleep(3) # Wait for page to load
            for index, comment in enumerate(comments):
                counter += 1
                comment_content = comment.find('div', class_='comment-text').text
                thumps_up_amount = comment.find('div', class_="rnr-com-like").text[1:-1]
                comments_array.append([comment_content, int(thumps_up_amount)])  # Add comment content and likes
                self.getCommentImages(comment, index, star)
                if counter >= 100:
                    break
            comments_array.append(counter)
            my_index = len(divs)-1
        return comments_array

    def getCommentImages(self, comment, index, star):
        comment_photos = comment.find('div', class_='comment-photos')
        if comment_photos:
            review_images = comment_photos.find_all('div', class_='item review-image')
            for image_index, review_image in enumerate(review_images):
                image_url = review_image.get('style', '')[23:-3]
                image_filename = f"{star}star_comment_{index + 1}_image_{image_index + 1}.jpg"
                self.UTILIZATION_OBJECT.downloadImage(image_url, image_filename)  # Download comment images

    def initiateScraping(self):
        LINKS = self.getProductLinks()
        self.getProductDetails(LINKS)
        self.UTILIZATION_OBJECT.create_output_jsonl()


if __name__ == '__main__':
    web_scraper = WebScraper()
    web_scraper.initiateScraping()  # Start scraping process
