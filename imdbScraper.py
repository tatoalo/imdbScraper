import requests, re, selenium, shutil, time
import _pickle as pickle
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

    browser.get("https://www.imdb.com/user/" + user_id)
    return browser


def visit_ratings(browser):
    ratings_link = browser.find_element_by_partial_link_text('See all')
    ratings_link.send_keys(Keys.RETURN)

    # Creating ratings data structure
    create_ratings_structure(browser)


def create_ratings_structure(browser):
    try:

        flagNext = True
        k = 0
        movieRating = dict()

        while flagNext:

            if k != 0:
                time.sleep(2)

            nextPage = browser.find_element_by_xpath("//a[@class='flat-button lister-page-next next-page']")
            ratings = browser.find_elements(By.XPATH, "//div[contains(@class, 'lister-item mode-detail')]")

            print("Found {} ratings".format(len(ratings)))

            downloadImages = False

            ratings_titles = []
            for i in ratings:
                if i.text != "":
                    title = i.text.split('\n')[0][3:]
                    a = i.find_element_by_css_selector('img').get_attribute('src')
                    personal_rating = i.text.split('\n')[3]
                    s = str(re.sub(r'\([^)]*\)', '', title).rstrip())
                    movieRating[s] = personal_rating
                    if downloadImages:
                        print("Trying to download: {}".format(a))
                        response = requests.get(a, stream=True)
                        with open('img/' + s + '.jpg', 'wb') as out_file:
                            shutil.copyfileobj(response.raw, out_file)
                    ratings_titles.append(title)

            if k != 1:
                k = k + 1
                nextPage.click()
            else:
                flagNext = False

        fileHandler = open(b"movieRatings.obj", "wb")
        pickle.dump(movieRating, fileHandler)
        fileHandler.close()

        # print(ratings_titles)
        # print(movieRating)

    except selenium.common.exceptions.NoSuchElementException:
        print('*** NOT FOUND ***')


def close_browser(browser):
    browser.close()
    browser.quit()


def main():
    # user_id = 'ur57539865'
    # user_id = 'ur59732679'
    user_id = 'ur18123905'

    b = init_chrome(user_id)
    visit_ratings(b)

    s = input('Close me?')

    if s == 'y':
        close_browser(b)


if __name__ == "__main__":
    main()
