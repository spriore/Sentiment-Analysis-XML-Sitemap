from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import urllib.request, string, pandas, time, re

start = time.time()

def html(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
    headers={"User-Agent":user_agent,} 
    request = urllib.request.Request(url,None,headers) #The assembled request
    response = urllib.request.urlopen(request) #URL phasing
    raw_html = response.read() #A copy of the raw HTML file
    return raw_html

url = input("Link to XML sitemap:")
file_path = input("CSV File name:")

#Build lexicon based dictionary
with open("SentiWordNet.txt") as fin:
    rows = ( line.split("\t") for line in fin )
    words= { row[4].split("#")[0]: (float(row[2]),float(row[3])) for row in rows }

#extract urls from xml sitemap
soup = BeautifulSoup(html(url), features="xml")
urls = [script.text for script in soup(["loc"])]

scores = {"URL":[], "pos-score":[], "neg-score": [], "obj-score": [], "cum-score": []}

for url in urls:
    
    try:
        #Preliminary cleaning
        soup = BeautifulSoup(html(url), "lxml")
        for script in soup(["head", "script", "style", "link", "meta", "footer", "#footer", "header", "#header"]):
            script.extract()

        #A copy of all text in HTML file w/o tags
        raw_text = soup.get_text(separator=" ")

        #Seperate words
        clean_text = word_tokenize(raw_text.lower())

		#Generate scores
        pos_score = sum(i[0] for i in (words.get(word,(0,0)) for word in clean_text))
        neg_score = sum(i[1] for i in (words.get(word,(0,0)) for word in clean_text))
        obj_score = sum((1-i[0]-i[1]) for i in (words.get(word,(0,0)) for word in clean_text))
        cum_score = pos_score - neg_score

		#Append scores
        if (cum_score != 0) & (pos_score * neg_score != 0):
            scores["URL"].append(url)
            scores["pos-score"].append(pos_score)
            scores["neg-score"].append(neg_score)
            scores["obj-score"].append(obj_score)
            scores["cum-score"].append(cum_score)
    except:
        continue

score_table = pandas.DataFrame(scores)
score_table.to_csv(file_path)

end = time.time()
print("it took {} minutes to complete".format((end - start)/60))
