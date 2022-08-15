import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common import exceptions

def create_webdriver_instance():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def login(driver,username,password,search_url):
    driver.get('https://twitter.com/i/flow/login')
    sleep(10)
    driver.find_element(By.NAME, 'text').send_keys(username)
    sleep(2)
    driver.find_element(By.NAME, 'text').send_keys(Keys.RETURN)
    sleep(5)
    driver.find_element(By.NAME, 'password').send_keys(password)
    sleep(5)
    driver.find_element(By.NAME, 'password').send_keys(Keys.RETURN)
    sleep(10)
    driver.get(search_url)
    sleep(5)   

def scroll_down_page(driver, last_position, num_seconds_to_load=5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    page_cards = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card,filepath):
    try:
        tweet_text = card.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
    except exceptions.NoSuchElementException:
        tweet_text = ""
    except exceptions.StaleElementReferenceException:
        return

    try:
        tweet_date = card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        tweet_date = ""
    except exceptions.StaleElementReferenceException:
        return
    
    try:
        links = card.find_elements(By.XPATH, './/a')
        for link in links:
            if 'status' in link.get_attribute('href'):
                tweet_link = link.get_attribute('href')
    except exceptions.NoSuchElementException:
        tweet_link = ""
    except exceptions.StaleElementReferenceException:
        return
        
    print(tweet_text)
    save_tweet_data_to_csv(tweet_text, tweet_date, tweet_link, filepath)


def save_tweet_data_to_csv(tweet, tweet_date, tweet_link, filepath):
    with open(filepath, 'a+', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([tweet_date])
        csvwriter.writerow([tweet_link])
        csvwriter.writerow([tweet])


def main(filepath):
    driver = create_webdriver_instance()

    username = input("Enter your username : ")
    password = input("Enter your password : ")
    search_url = input("Enter the User Profile Url : ")
    last_position = None
    end_of_scroll_region = False

    login(driver,username,password,search_url)

    while not end_of_scroll_region:
        cards = collect_all_tweets_from_current_view(driver)
        for card in cards:
            try:
                tweet = extract_data_from_current_tweet_card(card,filepath)
            except exceptions.StaleElementReferenceException:
                continue
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)

    sleep(60)
    driver.close()



if __name__ == '__main__':
    path = 'Twitter.csv'
    
    main(path)