import threading

import requests
import json
import shutil
import os
import queue

from selenium import webdriver

from selenium.webdriver.chrome.options import Options


USER_AGENT = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'}


class Downloader:
    def __init__(self, input_dict, cookies, pool_size):
        self.inputDict = input_dict
        #self.numQueries = len(self.inputDict.keys)
        self.cookies = cookies
        # Multithreading
        self.query_queue = queue.Queue(maxsize=pool_size)
        self.poolSize = pool_size
        self.currentQuery = None
        self.queryLeft = -1
        self.queryPage = -1
        self.queryIter = iter(self.inputDict.keys())
        self.currentQueryIdx = 0
        self.emptyCount = 0
        self._lock = threading.Lock()

    def startScaripng(self):
        # Build directories
        self.createDirectories()
        # Consume all queries
        self.consumeQueries()

    def createDirectories(self):
        dir_path = 'out'
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)
        for key in self.inputDict:
            os.mkdir('out/{}'.format(key))

    def consumeQueries(self):
        # Create process pool
        threads = [threading.Thread(target=self.processPage) for _ in range(self.poolSize)]
        # Start all threads
        [t.start() for t in threads]
        # Join all threads
        [t.join() for t in threads]

    def pageGenerator(self):
        with self._lock:
            if self.queryLeft > 0 and self.emptyCount < 10:
                self.queryPage += 10
            else:
                try:
                    self.currentQuery = next(self.queryIter)
                    self.currentQueryIdx += 1
                    print("Processing query \"{}\" - N.{}/{}"
                          .format(self.currentQuery, self.currentQueryIdx, len(self.inputDict)))
                except StopIteration:
                    return None, None
                self.queryLeft = self.inputDict[self.currentQuery]
                self.queryPage = 10
            return self.currentQuery, self.queryPage

    def processPage(self):
        driver = self.createDriver()

        while True:
            query, target_page = self.pageGenerator()
            if query == None:
                break

            response = self.queryRequest(query, target_page, driver)
            data_parsed = self.parseResponse(response)

            with self._lock:
                current = self.currentQuery
                if self.currentQuery != query:
                    continue
                left = self.queryLeft
                self.queryLeft -= len(data_parsed)
                if not data_parsed:
                    self.emptyCount += 1
            if left < len(data_parsed):
                data_parsed = data_parsed[:left]
            self.downladImages(data_parsed, query)
            if left > 0 and current == query:
                print("\t{}% completed.".format(round((1-(left/self.inputDict[query]))*100), 3))
        driver.quit()

    def createDriver(self):
        url = 'https://9gag.com/v1/search-posts?query=_&c=_'
        options = Options()
        #options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        for cookie in self.cookies:
            dict = {'name': cookie['name'], 'value': cookie['value']}
            driver.add_cookie(dict)
        return driver


    def queryRequest(self, query, page, driver):
        url = 'https://9gag.com/v1/search-posts?query={}&c={}'.format(query, page)
        driver.get(url)
        return json.loads(driver.find_element_by_tag_name("pre").text)

    def parseResponse(self, response):
        return [(obj['id'], obj['images']['image700']['url'])
                for obj in response['data']['posts'] if obj['type'] == 'Photo']

    def downladImages(self, images, target_dir):
        for id, url in images:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open('out/{}/{}.jpg'.format(target_dir, id), 'wb') as f:
                    f.write(r.content)
