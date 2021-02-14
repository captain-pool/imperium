import time
from selenium import webdriver
import pickle
import tqdm
import urllib.parse
import os
from selenium.webdriver.common.keys import Keys

path = "/Users/rick/selenium/chromedriver"
driver = webdriver.Chrome(path)

datadict = {}

driver.get("https://www.handspeak.com/word/search")

pagination_js = """
$.ajax({
        url:"/word/search/app/app-dictionary.php",
        method:"POST",
        data:{page:%d, query:""},
        success:function(data)
        { $('#content-wordlist').html(data);}
      });
"""

word_urls = []
start = 1
end = 496
datadictf = open("datadict.txt", "wb", buffering=0)
if not os.path.exists("wordurls.txt"):
  wordurls = open("wordurls.txt", "wb", buffering=0)
  for i in tqdm.tqdm(range(start, end)):
    anchors = driver.find_elements_by_css_selector("#content-wordlist>.col-abc>li>a")
    for anchor in anchors:
      href = anchor.get_attribute("href")
      text = anchor.get_attribute("text")
      if text.isalpha():
        word_urls.append(href)
        wordurls.write(("%s\n" % href).encode("utf-8"))
    if i < end - 1:
      driver.execute_script(pagination_js % (i + 1))
      time.sleep(3)
  wordurls.close()
else:
  word_urls = open("wordurls.txt", "r").read().split("\n")
  print(word_urls)

driver.set_page_load_timeout(3)
for url in tqdm.tqdm(word_urls):
  if not url:
    continue
  try:
    driver.get(url)
  except:
    driver.execute_script("window.stop();")
  video_url = driver.find_element_by_css_selector("#mySign").get_attribute("src")
  video_url_split = urllib.parse.urlsplit(video_url)
  video_name = video_url_split.path.split("/")[-1].split(".")[0]
  video_name = " ".join(video_name.split("-"))
  datadict[video_name] = video_url
  datadictf.write(("%s,%s\n" % (video_name, video_url)).encode("utf-8"))

datadictf.close()

with open("datadict.pkl", "wb") as f:
  pickle.dump(datadict, f)
