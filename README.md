# Trendyol Laptop Web Scraper

This project is a web scraper designed to extract detailed information about laptops listed on Trendyol. It collects product details, ratings, reviews, and images, and saves this data locally in a structured format.

## Features

- Scrapes laptop links based on the number of reviews.
- Extracts detailed information such as; product title, price, question-count, favourites-count, comment-count, overall rating score, rating distribution, and seller name.
- Downloads product images and stores them locally.
- Collects and filters product comments based on ratings.
- Downloads images shared by users in comments section.
- Saves product data in JSON format.

## Installation

### Prerequisites

- Python
- Google Chrome browser
- ChromeDriver

### How to Run the Script

- Enter the following command to the terminal (command prompt)
- python main.py

## Output

- After the program is run, it creates a folder named 'products' in the current folder. There are as many folders in this folder as there are products that meet the conditions (lapptop_1, laptop_2...).
- Each product has an 'images' folder and a 'product_info.json' folder in its own folder. The 'images' folder contains both product images and images shared in the comments. 
- The product images are named as "product_image_index.jpg". Other images are named as "(1,5)star_comment_index_image_index.jpg".
- Information about the product is kept in the file named 'product_info.json'. The value in index number 0 of the "Rating Distribution" array represents the number of 5 stars, and the value in index number 4 represents the number of 1 stars.
- In the comments array, 1-star comments are listed first and after each comment content, the number of thumps-up for that comment is found. When the comment category is finished, the number of comments is added into the array.
- "output.jsonl" file contains the name of the products and the relative path to the images folder of these products.

## Feature Ideas

- Multi-thread approaches can be used to speed up the scraping process.