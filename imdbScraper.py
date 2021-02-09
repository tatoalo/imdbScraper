import _pickle as pickle
import re
import requests
import selenium
import shutil
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def init_chrome(user_id):
    opt_args = Options()
    opt_args.add_argument("--no-sandbox")
    opt_args.add_argument("--remote-debugging-port=9222")
    opt_args.add_argument("--headless")
    opt_args.add_argument("--window-size=1920,1080")
    opt_args.add_argument("--disable-gpu")
    b = webdriver.Chrome(options=opt_args)

    b.get("https://www.imdb.com/user/" + user_id)
    return b


def visit_ratings(b):
    ratings_link = b.find_element_by_partial_link_text('See all')
    ratings_link.send_keys(Keys.RETURN)

    # Creating ratings data structure
    create_ratings_structure(b)


def create_ratings_structure(b):
    try:

        flagNext = True
        k = 0
        movieRating = dict()
        downloadImages = True
        errorPics = 0

        if downloadImages:
            if os.system("rm img/*") != 0:
                print("Folder was already empty")
            else:
                print("Folder content cleaned")

        while flagNext:

            if k != 0:
                time.sleep(2)

            nextPage = b.find_element_by_xpath("//a[@class='flat-button lister-page-next next-page']")
            ratings = b.find_elements(By.XPATH, "//div[contains(@class, 'lister-item mode-detail')]")

            print("Found {} ratings".format(len(ratings)))

            ratings_titles = []
            for i in ratings:
                # print("Handling lazy loading...")
                b.execute_script("window.scrollTo(0, window.scrollY + 200)")
                if i.text != "":
                    title = i.text.split('\n')[0][3:]
                    a = i.find_element_by_css_selector('img').get_attribute('src')
                    personal_rating = i.text.split('\n')[3]
                    s = str(re.sub(r'\([^)]*\)', '', title).rstrip())
                    movieRating[s] = personal_rating
                    if downloadImages:
                        print("Trying to download: {}".format(a))
                        if ".png" in a:
                            print("Scrolling down...")
                            b.execute_script("window.scrollTo(0, window.scrollY + 300)")
                            a = i.find_element_by_css_selector('img').get_attribute('src')
                            print(f"Scrolled to: {a}")
                            possibleErrorPic = 0
                            while ".png" in a:
                                if possibleErrorPic == 3:
                                    errorPics = errorPics + 1
                                    print("**** OUT OF CONTROL ERROR! ****")
                                    break
                                print("*** Scrolling again ***")
                                b.execute_script("window.scrollTo(0, window.scrollY + 20)")
                                a = i.find_element_by_css_selector('img').get_attribute('src')
                                possibleErrorPic = possibleErrorPic + 1
                                print("*** ONCE AGAIN ***")
                        response = requests.get(a, stream=True)
                        s = s.strip()
                        finalFileName = ''
                        if '/' in s:
                            t = s.split('/')
                            for _ in t:
                                finalFileName += ' ' + _
                            s = finalFileName.strip()
                        if '.' in s:
                            s = s.strip('.').strip()
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
        shutil.copy("movieRatings.obj", "/Users/apogliaghi/Vagrant/vagrant_shared_folder/movieRatings.obj")

        if errorPics != 0:
            print(f"*** Found {errorPics} null images! ***")

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
    user_id = 'ur57539865'

    test = True

    if not test:
        start_time = time.time()
        b = init_chrome(user_id)
        visit_ratings(b)
        print("--- %s seconds ---" % (time.time() - start_time))

        s = input('Close me?')

        if s == 'y':
            close_browser(b)
    else:
        fileHandler = open(b"movieRatings.obj", "rb")
        diffList = pickle.load(fileHandler)
        fileHandler.close()

        t = os.listdir("img/")

        print(len(diffList), len(t))

        for _ in t:
            elementToRemove = _.split('.jpg')[0]
            try:
                del(diffList[elementToRemove])
            except KeyError as e:
                print(f"missing movie: {e} in movieRatings data structure.")


if __name__ == "__main__":
    main()
