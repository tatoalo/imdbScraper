import _pickle as pickle
import re
import requests
import shutil
import time
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
        movieRating = dict()
        downloadImages = False
        errorPics = 0

        if downloadImages:
            if os.system("rm img/*") != 0:
                print("Folder was already empty")
            else:
                print("Folder content cleaned")

        while flagNext:

            time.sleep(2)

            try:
                nextPage = b.find_element_by_xpath("//a[@class='flat-button lister-page-next next-page']")
            except NoSuchElementException:
                print("Visiting last rating page.")
                flagNext = False

            ratings = b.find_elements(By.XPATH, "//div[contains(@class, 'lister-item mode-detail')]")

            print("Found {} ratings".format(len(ratings)))

            ratings_titles = []
            for i in ratings:
                # print("Handling lazy loading...")
                b.execute_script("window.scrollTo(0, window.scrollY + 200)")
                if i.text != "" and 'Episode' not in i.text:
                    ID = i.find_element_by_xpath(".//div[@class='lister-item-image "
                                                 "ribbonize']").get_attribute('data-tconst')

                    title = i.text.split('\n')[0][3:]
                    a = i.find_element_by_css_selector('img').get_attribute('src')

                    data_type = i.text.split('\n')[1].split('|')[0]
                    director = ''
                    actors = ''
                    runtime = ''
                    if 'TV' in data_type:
                        data_type = 'tv_series'
                        if 'Stars' in str(i.text):
                            actors = i.text.split('\n')[len(i.text.split('\n'))-2].split("Stars: ")[1].split(',')
                            actors = [a.strip() for a in actors]
                    else:
                        data_type = 'movie'
                        runtime = i.text.split('\n')[1].split('|')[len(i.text.split('\n')[1].split('|'))-2].strip()
                        people = i.text.split('\n')[len(i.text.split('\n')) - 2].split('|')
                        if 'Prime' in str(people):
                            people = i.text.split('\n')[len(i.text.split('\n')) - 4].split('|')
                        # Certain docs have no directors data
                        if len(people) == 1:
                            actors = people[0].split('Stars: ')[1].split(',')
                            actors = [a.strip() for a in actors]
                        else:
                            # Freaking Coen brothers! :P
                            if 'Directors' in str(people):
                                director = people[0].split('Directors: ')[1].strip()
                            else:
                                director = people[0].split('Director: ')[1].strip()
                            actors = people[1].split('Stars: ')[1].split(',')
                            actors = [a.strip() for a in actors]

                    year = re.search(r'\(([^)]+)\)', title)[1]
                    personal_rating = i.text.split('\n')[3]
                    IMDB_rating = i.text.split('\n')[2]
                    rated_on = i.text.split('\n')[5].split('on')[1].strip()
                    genre = i.text.split('\n')[1].split('|')[len(i.text.split('\n')[1].split('|'))-1].strip()

                    s = str(re.sub(r'\([^)]*\)', '', title).rstrip())
                    s = s.strip('.').strip()

                    title = title.strip('.').strip()

                    movieRating[ID] = {
                        'ID': ID,
                        'type': data_type,
                        'title': s,
                        'genre': genre,
                        'year': year,
                        'personal_rating': personal_rating,
                        'IMDB_rating': IMDB_rating,
                        'rated_on': rated_on,
                        'actors': actors,
                        'director': director,
                        'runtime': runtime
                    }

                    if downloadImages:
                        # print("Trying to download: {}".format(a))
                        if ".png" in a:
                            print("Scrolling down...")
                            b.execute_script("window.scrollTo(0, window.scrollY + 300)")
                            a = i.find_element_by_css_selector('img').get_attribute('src')
                            # print(f"Scrolled to: {a}")
                            possibleErrorPic = 0
                            while ".png" in a:
                                if possibleErrorPic == 3:
                                    errorPics = errorPics + 1
                                    # print("**** OUT OF CONTROL ERROR! ****")
                                    break
                                # print("*** Scrolling again ***")
                                b.execute_script("window.scrollTo(0, window.scrollY + 20)")
                                a = i.find_element_by_css_selector('img').get_attribute('src')
                                possibleErrorPic = possibleErrorPic + 1
                                # print("*** ONCE AGAIN ***")
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

            if flagNext:
                nextPage.click()

        fileHandler = open(b"movieRatings.obj", "wb")
        pickle.dump(movieRating, fileHandler)
        fileHandler.close()
        shutil.copy("movieRatings.obj", "/Users/apogliaghi/Vagrant/vagrant_shared_folder/movieRatings.obj")

        if errorPics != 0:
            print(f"*** Found {errorPics} null images! ***")

        # print(ratings_titles)
        # print(movieRating)

    except NoSuchElementException:
        print('*** NOT FOUND ***')


def close_browser(browser):
    browser.close()
    browser.quit()


def main():
    user_id = 'ur57539865'

    start_time = time.time()
    b = init_chrome(user_id)
    visit_ratings(b)
    print("--- %s seconds ---" % (time.time() - start_time))
    close_browser(b)


if __name__ == "__main__":
    main()
