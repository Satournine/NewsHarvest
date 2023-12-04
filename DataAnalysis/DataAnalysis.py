from pymongo import MongoClient
from collections import Counter
import re
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import seaborn as sns
import logging


def get_news_articles(collection):  # Retrieves all news articles from a MongoDB collection
    return collection.find({}, {'text': 1, '_id': 0})


def get_extra_stopwords(filepath):  # Reads a file containing stopwords
    extra_stop = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            extra_stop.append(line.strip())
    return extra_stop


def filter_words(news_articles, stop_words, extra_stop):  # Filters out stopwords from the news articles
    words = []
    for data in news_articles:
        article_words = re.findall(r'\w+', data['text'].lower())
        filtered_words = [word for word in article_words if word not in stop_words]
        final_words = [word for word in filtered_words if word not in extra_stop]
        words.extend(final_words)
    return words


def insert_db(collection, word_frequencies):  # Inserts word frequency data to MongoDB
    for word, count in word_frequencies:
        word_data = {"word": word, "count": count}
        collection.insert_one(word_data)


def plot_word_frequency(word_frequencies):  # Plots the frequency of words using seaborn
    words, counts = zip(*word_frequencies)
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(counts), y=list(words))

    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title('Top 10 Most Common Words')
    plt.show()


def print_grouped_data_by_update_date(news_collection):  # groups docs by their update date
    pipeline = [
        {
            "$group": {
                "_id": "$update_date",
                "articles": {
                    "$push": {
                        "url": "$url",
                        "header": "$header",
                    }
                }
            }
        },
        {"$sort": {"_id": 1}}  # 1 for ascending, -1 for descending
    ]
    try:
        grouped_data = news_collection.aggregate(pipeline)
        for data in grouped_data:
            logging.info(f"Update Date: {data['_id']}")
            for article in data['articles']:
                logging.info(f"URL: {article['url']}, Header: {article['header']}")
    except Exception as e:
        print(f"Error in grouping data: {e}")


def main():
    # Setting up MongoDB connection
    client = MongoClient("mongodb://localhost:27017")
    db = client["orkun_tuna"]
    news_collection = db["news"]
    word_frequency_collection = db["word_frequency"]
    # Configuring logging
    logging.basicConfig(filename='data_analysis.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Getting stopwords
    turkish_stopwords = stopwords.words('turkish')
    extra_stopwords = get_extra_stopwords('stopwords.txt')
    # Retrieving news articles
    news_articles = get_news_articles(news_collection)
    # Processing words and counting frequencies
    words = filter_words(news_articles, turkish_stopwords, extra_stopwords)
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    # Inserting data into DB and plotting
    insert_db(word_frequency_collection, most_common_words)
    plot_word_frequency(most_common_words)

    print_grouped_data_by_update_date(news_collection)


if __name__ == "__main__":
    main()
