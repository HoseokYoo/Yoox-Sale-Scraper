from bs4 import BeautifulSoup
from config import BRAND_NAMES, BRAND_NUMBERS, DESIRED_DISCOUNT, MINUTES_BETWEEN_SEARCH
from requests_html import HTMLSession
import time
import difflib
import os
import shutil
import datetime

session = HTMLSession()

def find_items():
    # Clears listing text file if it exists
    file_to_delete = open("items.txt", "w", encoding="utf8")
    file_to_delete.close()

    found_item_count = 0
    all_found_items = []
    category_name = '니트%20&%20스웻셔츠_mc'
    # category_name = '코트%20&%20자켓_mc'
    # category_name = '스니커즈_c'
    # category_name = '주얼리_mc'
    # attributes = '%7b%27ctgr%27%3a%5b%27gll%27%5d%7d'
    # attributes = '%7b%27mtrl%27%3a%5b%27lpc%27%5d%7d' # 알파카
    # attributes = '%7b%27mtrl%27%3a%5b%27cshmr%27%5d%7d' #캐시미어
    # attributes = '%7b%27ctgr%27%3a%5b%27prk1%27%5d%7d' # 파카
    # attributes = '%7b%27ctgr%27%3a%5b%27mglncchm%27%5d%7d' # 캐시미어 니트
    attributes = '%7b%27ctgr%27%3a%5b%27crdgn%27%5d%7d' # 가디건

    for brand_name, brand_num in zip(BRAND_NAMES, BRAND_NUMBERS):
        print(str(datetime.datetime.now()), "-", f"Searching {brand_name} items")

        for page_number in range(1, 100):
            # url = f"https://www.yoox.com/kr/남성/shoponline/{brand_name}_md/{page_number}#/d={brand_num}&dept=men&gender=U&page={page_number}&season=X&sort=3"
            url = f"https://www.yoox.com/kr/남성/shoponline/{category_name}/?d={brand_num}&dept=men&gender=U&page={page_number}&season=X&sort=3&attributes={attributes}"
            response = session.get(url, timeout=60)

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, "lxml")

            # Ends loop when we reach a page that contains no items
            if soup.find("div", class_="itemData text-center") == None:
                break

            # Find all item listing
            items = soup.find_all("div", class_="col-8-24")
            for item in items:
                # Filters out non item elements
                if item.find("div", class_="itemData text-center") == None:
                    break

                # Filters out sold out items
                if "SOLD OUT" not in item.find("div", class_="price").text.strip():
                    sale_percentage_element = item.find("span", class_="element")
                    sale_percentage = None

                    if sale_percentage_element:
                        sale_percentage = int(sale_percentage_element.text.strip().split("%")[0][1:])

                    # Filters out items not on sale
                    if sale_percentage and sale_percentage >= DESIRED_DISCOUNT:
                        brand = item.find("div", class_="brand font-bold text-uppercase").text.strip()
                        type = item.find("div", class_="microcategory font-sans").text.strip()
                        sale_percentage = item.find("span", class_="element").text.strip()
                        old_price = item.find("span", class_="oldprice text-linethrough text-light").text.strip()
                        new_price = item.find( "div", class_="retail-newprice font-bold").text.strip()
                        url = "https://www.yoox.com" + item.find("a", class_="itemlink")["href"]
                        # image = item.find('img', class_="front").get('src')

                        # Want to sort items by price. Turn the current price into an int for sorting
                        sort_value = int(new_price.split(" ")[1].split(".")[0].replace(",",""))

                        # Put item data into a list containing all items so we can sort later
                        all_found_items.append([sort_value, brand, type, sale_percentage, old_price, new_price, url])

                        found_item_count += 1

    # Sort all items found from lowest price to highest price. Then we output onto text file
    all_found_items.sort()
    for item in all_found_items:
        with open("items.txt", "a", encoding="utf8") as f:
            f.write(f"Brand:       {item[1]} \n")
            f.write(f"Item Type:   {item[2]} \n")
            f.write(f"Sale:        {item[3]} \n")
            f.write(f"Old Price:   {item[4]} \n")
            f.write(f"New Price:   {item[5]} \n")
            f.write(f"URl:         {item[6]} \n\n")
            # f.write(f"Image:       {item[7]} \n\n")

    print(str(datetime.datetime.now()), "-", f"{found_item_count} total items found at {DESIRED_DISCOUNT}% off.")

def get_file_differences(file1, file2) -> bool:
    '''
    Get lines in file2 that are not in file1 as opposed to overall differences between the two txt files
    '''

    with open(file1, 'r', encoding="utf8") as f1, open(file2, 'r', encoding="utf8") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff = difflib.ndiff(lines1, lines2)
    diff_lines = [line for line in diff if line.startswith('+ ')]
    if len(diff_lines) > 0:
        with open("new_sales.txt", "w", encoding="utf8") as f:
            f.write(str(datetime.datetime.now()) + f"\n")
            for line in diff_lines:
                f.write(line)
        shutil.copyfile('new_sales.txt', f"./logs/{str(time.time())}.txt")
        return True
    return False

def get_new_sale_items():
    # Specify the file paths
    file1 = "old_items.txt"  # Previous data
    file2 = "items.txt"  # Updated data

    # Call the function to get the differences between the two text files.
    new_sales = get_file_differences(file1, file2)

    if new_sales == True:
        os.system("notepad.exe new_sales.txt")
        # 윈도우용

    # Update the text file for old_items to our new list of items
    os.remove("old_items.txt")
    shutil.copyfile("items.txt", "old_items.txt")

if __name__ == "__main__":
    while True:
        find_items()
        get_new_sale_items()
        time_wait = MINUTES_BETWEEN_SEARCH
        print(str(datetime.datetime.now()), "-", f"Searching again in {time_wait} minute...")
        time.sleep(time_wait * 60)