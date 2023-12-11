import nltk
import requests
from bs4 import BeautifulSoup
from nltk import stem
import time
nltk.download('punkt')

def clean_word(input_text):
    # 余分な空白を削除し、"例文帳に追加"の重複を排除
    cleaned_text = ' '.join(input_text.strip().split()).replace('例文帳に追加', ' ')
    return cleaned_text

def get_weblio_sentence(word):
    url = f"https://ejje.weblio.jp/sentence/content/{word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    qotCJ_elements = soup.find_all("div", class_="qotC")
    return qotCJ_elements

def get_hatsuon_info(word):
    url = f"https://en.hatsuon.info/word/{word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    hat = soup.find_all("div", class_="font4")
    men = soup.find_all("div", class_="font1")
    return hat, men

def display_results(word, hat, lists, men):
    print(f"\n------{word} 取得結果------")
    print(hat)
    print("------例文------")
    for i in lists:
        print(i)
        print("\n")
    print("------意味------")
    print(men)

def main():
    while True:
        en = input("Please input word (finish 'exit' ): ")
        if en.lower() == 'exit':
            break

        morph = nltk.word_tokenize(en)
        for i in morph:
            if i == ".":
                pass
            stemmer = stem.PorterStemmer()
            tan = stemmer.stem(i)
            weblio_sentences = get_weblio_sentence(i)
            hat, men = get_hatsuon_info(i)
            lists = []

            for j in range(3):
                try:
                    strdata = clean_word(weblio_sentences[j].text)
                except:
                    strdata = "No data"
                finally:
                    lists.append(strdata)
            try:
                hat = hat[0].text
                hat = hat.replace("音声を再生", "")
            except:
                hat = "No data"
            try:
                men = men[0].text
            except:
                men = "No data"

            weblio_stemmed_sentences = get_weblio_sentence(tan)
            hat2, men2 = get_hatsuon_info(tan)
            lists2 = []

            for j in range(3):
                try:
                    strdata = clean_word(weblio_stemmed_sentences[j].text)
                except:
                    strdata = "No data"
                finally:
                    lists2.append(strdata)

            try:
                hat2 = hat2[0].text
                hat2 = hat2.replace("音声を再生", "")
            except:
                hat2 = "No data"

            try:
                men2 = men2[0].text
            except:
                men2 = "No data"

            display_results(f"単語無修正 {i}", hat, lists, men)
            display_results(f"単語修正 {tan}", hat2, lists2, men2)
            time.sleep(1)

if __name__ == "__main__":
    print("HEY!! ENGLISH-CUI-SYSTEM WECLOME POWER BY KAZUMA")
    main()