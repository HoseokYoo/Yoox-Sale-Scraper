from selenium import webdriver
from time import sleep
import urllib.parse
import re
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()
options = webdriver.ChromeOptions()
# options.add_argument('--no-sandbox')
# options.add_argument('--headless')

def screen_shot(url):
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)
    driver.get(url)

    # driver.get_screenshot_as_file('./images/' + urllib.parse.quote_plus(url) + '.png')
    driver.save_screenshot('./images/' + urllib.parse.quote_plus(url) + '.png')
    print('./images/' + urllib.parse.quote_plus(url) + '.png')
    driver.quit()


pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

with open('new_sales.txt', encoding='utf8') as f:
    Lines = f.readlines()
    for line in Lines:
        m = re.findall(pattern, line)
        if m:
            url = '\n'.join([x[0] for x in m])
            screen_shot(url)


