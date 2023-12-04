# NewsHarvest

## Description
This project involves web scraping and data analysis. `DataHarvest.py` is responsible for scraping news articles from a specified URL and storing them in a MongoDB database. `DataAnalysis.py` performs analysis on the scraped data, focusing on word frequency analysis and grouping data by update date.

## Installation
To set up this project, follow these steps:

1. **Clone the Repository:**
git clone https://github.com/Satournine/NewsHarvest

2. **Install Required Libraries:**
You need Python 3.x and the following libraries: `bs4`, `requests`, `pymongo`, `nltk`, `matplotlib`, `seaborn`. Install them using pip: pip install beautifulsoup4 requests pymongo nltk matplotlib seaborn

3. **MongoDB:**
Ensure MongoDB is installed and running on your system.

## Usage

### Data Harvesting
Run `DataHarvest.py` to scrape news data from the web and store it in MongoDB.

 `python DataHarvest.py `

### Data Analysis
Run `DataAnalysis.py` to analyze the stored data. It performs:
- Word frequency analysis on the news text.
- Plots the most common words.
- Groups news articles by their update date and logs them under its directory in ascending order.
  
 `python DataAnalysis.py `


### Stopwords File
Create a `stopwords.txt` file in the project root with additional stopwords to be excluded from the analysis.

## Data Structure
The MongoDB database will have three main collections:
1. `news`: Stores the scraped news articles.
2. `word_frequency`: Stores the word frequency analysis results.
3. `stats`: Stores the stats of data scraping.

![Alt text](https://github.com/Satournine/NewsHarvest/assets/32436768/2904b757-375a-4045-ac28-39603b05e0d0)
   
Each document in the `news` collection has the following structure:
- `url`: The URL of the news article.
- `header`: The header of the news article.
- `summary`: A summary of the article.
- `text`: The full text of the article.
- `img_url_list`: List of image URLs in the article.
- `publish_date`: The publish date of the article.
- `update_date`: The last update date of the article.

## Word Frequency Graph
`DataAnalysis.py` generates a bar graph displaying the top 10 most common words in the scraped news articles.

![Alt text](https://github.com/Satournine/NewsHarvest/assets/32436768/14e723b1-3f3b-44aa-9217-a391d6165dfe)

## Logging
`DataHarvest.py` logs its operations, including successful data inserts and errors, into a `logs.log` file in the `logs` directory.


