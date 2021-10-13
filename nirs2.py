import csv
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool


def get_all_pages():
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    r = requests.get(url="https://md.tomsk.ru/feedback/", headers=headers)

    if not os.path.exists("data"):
        os.mkdir("data")

    with open("data/page_1.html", "w") as file:
        file.write(r.text)

    with open("data/page_1.html") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    pages_count = int(soup.find("div", class_="navigation-pages").find_all("a")[-2].text)

    for i in range(1, pages_count + 1):
        url = f"https://md.tomsk.ru/feedback/?PAGEN_1={i}"

        r = requests.get(url=url, headers=headers)

        with open(f"data/page_{i}.html", "w") as file:
            file.write(r.text)

        time.sleep(2)

    return pages_count + 1


def collect_data(pages_count):
    cur_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"data_{cur_date}.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Вопрос",
                "Ссылка"
            )
        )

    data = []
    for page in range(1, pages_count):
        with open(f"data/page_{page}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_cards = soup.find_all("div", class_="rshift_feedback_item")
        NONE = "none"
        for item in items_cards:
            question_text = item.find("div", class_="rshift_feedback_author_text").text
            a_element = item.find("a")
            try:        	
            	question_url = f'https://md.tomsk.ru{a_element.get("href")}'

            	data.append(
                	{
                  	  "question_article": question_text,
                  	  "question_url": question_url,
                	}
            	)

            	with open(f"data_{cur_date}.csv", "a") as file:
            
                	writer = csv.writer(file)

                	writer.writerow(
                    		(
                        	question_text,
                        	question_url,
                    		)
                	)
            except AttributeError:            
            	data.append(
                	{
                  	  "question_article": question_text,
                  	  "question_url": NONE,
                	}
            	)

            	with open(f"data_{cur_date}.csv", "a") as file:
            
                	writer = csv.writer(file)

                	writer.writerow(
                    		(
                        	question_text,
                        	NONE,
                    		)
                	)
            
            
        print(f"[INFO] Обработана страница {page}/5")


def main():
    start_time = time.monotonic()
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)


    print('время работы прораммы ' + str(time.monotonic() - start_time)) # вывод затраченного времени
    
    
if __name__ == '__main__':
    main()
