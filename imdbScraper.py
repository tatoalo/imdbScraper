import time
import selenium
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def init_chrome(user_id):
    opt_args = Options()
    opt_args.add_argument("--no-sandbox")
    # opt_args.add_argument("--remote-debugging-port=9222")
    opt_args.add_argument("--headless")
    opt_args.add_argument("--window-size=1920,1080")
    opt_args.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=opt_args)
    # browser.maximize_window()
    # browser = webdriver.Chrome()
    browser.get("https://www.imdb.com/user/"+user_id)
    return browser


def visit_ratings(browser):
    ratings_link = browser.find_element_by_partial_link_text('See all')
    ratings_link.send_keys(Keys.RETURN)

    # Creating ratings data structure
    create_ratings_structure(browser)


def create_ratings_structure(browser):

    try:
        # ratings_container = browser.find_elements(By.XPATH, "//div[@id='ratings-container']")

        # ratings_number = browser.find_element(By.XPATH, "//span[@id='lister-new-size]").get_attribute("value")
        #
        # if int(ratings_number) is 240:
        #     print("Correct #ratings!")
        #
        ratings = [browser.find_elements(By.XPATH, "//div[@class='lister-item mode-detail']")]

        for i in ratings:
            # "//form[@id='loginForm']/input[1]")
            t = browser.find_element(By.XPATH, "//h3[@class='lister-item-header']/a")
            print(t.text)

        # k = 0
        # for i in t:
        #     k += 1
        #     print(i.text)
        #
        # print('/n.{}'.format(k))
    except selenium.common.exceptions.NoSuchElementException:
        print('*** NOT FOUND ***')


def close_browser(browser):
    browser.close()
    browser.quit()


def main():

    # user_id = 'ur57539865'
    user_id = 'ur59732679'

    b = init_chrome(user_id)
    visit_ratings(b)

    s = input('Close me?')

    if s is 'y':
        close_browser(b)


if __name__ == "__main__":
    main()