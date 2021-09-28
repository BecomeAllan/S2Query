import requests
import json
import multiprocessing as mp
import os
# import numpy as np
import pandas as pd
import re
import ast
from pathlib import Path


from time import sleep, time


def timer(fun):
  def warper(*args,**kwargs):
    start = time()
    d = fun(*args,**kwargs)
    end = time()
    print(f"[{fun.__name__}]>> Demorou {round(end-start,2)}s")
    return d
  return warper



class SearchWeb():
  def __init__(self, search="Machine Learning+Deep Learning", poolCPU = 4, sleeptry=5, save = False, **kwargs):
     
    self.sleeptry = sleeptry
    self.poolCPU = poolCPU
    self.saveName = kwargs.get('Savename', "Data")

    self.badcall = []
    self._start = True

    self.saveFile = save
    self._search = search
    self._sort = kwargs.get('sort', "relevance")
    self._authors = kwargs.get('authors', [])
    self._coAuthors = kwargs.get('coAuthors', [])
    self._venues = kwargs.get('venues', ['PloS one', 'AAAI', 'Scientific reports', 'IEEE Access', 'ArXiv', 'Expert Syst. Appl.', 'ICML', 'Neurocomputing', 'Sensors', 'Remote. Sens.'])
    self._yearFilter = kwargs.get('yearFilter', None) # {"min": 2008,"max": 2021}
    self._requireViewablePdf = kwargs.get('requireViewablePdf', False)
    self._publicationTypes = kwargs.get('publicationTypes', ["ClinicalTrial", "CaseReport", "Editorial","Study","Book","News","Review","Conference","LettersAndComments","JournalArticle"])
    self._fieldsOfStudy = kwargs.get('fieldsOfStudy', ["biology","art","business","computer-science","chemistry","economics","engineering","environmental-science","geography","geology","history","materials-science","mathematics","medicine","philosophy","physics","political-science","psychology","sociology"])
    self._useFallbackRankerService = kwargs.get('useFallbackRankerService', False)
    self._useFallbackSearchCluster = kwargs.get('useFallbackSearchCluster', False)
    self._hydrateWithDdb = kwargs.get('hydrateWithDdb', True)
    self._includeTldrs = kwargs.get('includeTldrs', True)
    self._performTitleMatch = kwargs.get('performTitleMatch', True)
    self._includeBadges = kwargs.get('includeBadges', True)
    self._tldrModelVersion = kwargs.get('tldrModelVersion', 'v2.0.0')
    self._getQuerySuggestions = kwargs.get('getQuerySuggestions', False)


    self.post = {
    "page": 1, 
    "pageSize": 10,
    "queryString": self._search,
    "sort": self._sort,
    "authors": self._authors,
    "coAuthors": self._coAuthors,
    "venues": self._venues,
    "yearFilter": self._yearFilter,
    "requireViewablePdf": self._requireViewablePdf,
    "publicationTypes": self._publicationTypes,
    "externalContentTypes": [],
    "fieldsOfStudy": self._fieldsOfStudy,
    "useFallbackRankerService": self._useFallbackRankerService,
    "useFallbackSearchCluster": self._useFallbackSearchCluster,
    "hydrateWithDdb": self._hydrateWithDdb,
    "includeTldrs": self._includeTldrs,
    "performTitleMatch": self._performTitleMatch,
    "includeBadges": self._includeBadges,
    "tldrModelVersion": "v2.0.0",
    "getQuerySuggestions": self._getQuerySuggestions,
    }

  
  
  def _paperExtract(self, data):
    p = {
        "authors": [author[0]['name'] for author in data.get('authors',[{'name':None},None])],
        "id": data.get('id',None),
        "socialLinks": data.get('socialLinks',None),
        "title": data.get('title',{'text':None})['text'],
        "paperAbstract": data.get('paperAbstract',{'text':None})['text'],
        "year": data.get('year',{'text':None})['text'],
        "venue": data.get('venue',{'text':None})['text'],
        "citationContexts":data.get('citationContexts',None),
        "citationStats": data.get('citationStats',None),
        "sources":data.get('sources',None),
        "externalContentStats":data.get('externalContentStats',None),
        "journal":data.get('journal',None),
        "presentationUrls":data.get('presentationUrls',None),
        "links": data.get('links',None),
        "primaryPaperLink": data.get('primaryPaperLink',None),
        "alternatePaperLinks": data.get('alternatePaperLinks',None),
        "entities": [author['name'] for author in data.get('entities',[{'name':None}])],
        "entityRelations": data.get('entityRelations',None),
        "blogs":data.get('blogs',None),
        "videos":data.get('videos',None),
        "githubReferences": data.get('githubReferences',None),
        "scorecardStats": data.get('scorecardStats',None),
        "fieldsOfStudy":data.get('fieldsOfStudy',None),
        "pubDate":data.get('pubDate',None),
        "pubUpdateDate":data.get('pubUpdateDate',None),
        "badges":data.get('badges',None),
        "tldr":data.get('tldr',None)
        }
    return p

  def _query(self, page):
    url = "https://www.semanticscholar.org/api/1/search"
    post = self.post.copy()
    post["page"] = page
    try:
      res = requests.post(url, json=post, timeout=15)
      res.encoding = 'utf-8'
      return [res, page, res.status_code]
    except:
      return [None, page, 400 ]
      

  def _json(self, res):
#     print(res.text)
    return json.loads(res.text).copy()

    # c['querySuggestions']
    # c['totalPages']
    # c['totalResults']
  def save(self, name, data):
    try:
      with open(f'./{name}.json', 'w',encoding='UTF-8') as fp:
          json.dump(data, fp)
    except:
      print("[Save]>> Error to save the data.")
  
  def load_json(self, path):
    try:
      with open(f'{path}', 'r', encoding='UTF-8') as fp:
          return json.load(fp)
    except:
      print("[load_json]>> Error to load json file.")
    
  def _startFile(self, find):
    jsonFile = Path(f"./{self.saveName}.json")
    textFile = Path(f"./{self.saveName}.text")
    
    if jsonFile.is_file():
      if find:
        try:
          print(f"[_startFile] >> Loading ./{self.saveName}.json")
          with open(f'./{self.saveName}.json', 'r',encoding='UTF-8') as f:
            data = json.load(f)
          print(f"[Create] >> Creating a ./{self.saveName}.text file to save data.")
          with open(f'./{self.saveName}.text', 'w',encoding='UTF-8') as fp:
            fp.write("{\"Results\": [")
        
        # print(data['Results'])
          self._save(data['Results'])
        except:
          print(f"[_startFile] >> Fail to load ./{self.saveName}.json")
          try:
            # print(f"[Create] >> Creating a ./{self.saveName}.text file to save data.")
            with open(f'./{self.saveName}.text', 'w', encoding='UTF-8') as fp:
              fp.write("{\"Results\": [")
          except:
            print("[Create] >> Fail")
      else:
        return False
    else:
      try:
        print(f"[Create] >> Creating a ./{self.saveName}.text file to save data.")
        with open(f'./{self.saveName}.text', 'w',encoding='UTF-8') as fp:
          fp.write("{\"Results\": [")
      except:
        print("[Create] >> Fail")
    return True


  def _save(self, check_point):
    if str(check_point) == '[]' or str(check_point) == '[,]':
      return _
    else:
      text = str(check_point)

      text = re.sub('^\[', '', text)
      text = re.sub('\]$', '', text)

      
      with open(f'./{self.saveName}.text', 'a', encoding='utf-8') as fp:
        fp.write(text)
          # json.dump(self.all['Results'], fp)
      print(f"[Save] >> Saving check_point at current directory, ./{self.saveName}.text")
      

  def _endFile(self):
    # ast.literal_eval(text)
    try:
      with open(f'./{self.saveName}.text', 'a', encoding='UTF-8') as fp:
        fp.write(']}')
      
      try:
        with open(f'./{self.saveName}.text', 'r', encoding='UTF-8') as fp:
          text = fp.read()
          text_dict = ast.literal_eval(text)
        
      
      # os.rename(f'./{self.saveName}.text', f'./{self.saveName}.json')
      # os.remove(f"./{self.saveName}.text")
      # print(text_dict)
        with open(f'./{self.saveName}.json', 'w', encoding='UTF-8') as fp:
          json.dump(text_dict, fp)
        print(f"[Close] >> Closed and save in ./{self.saveName}.json file the data.")
      except:
        print(f"[Close] >> Fail to save the data ./{self.saveName}.json file.")

    except:
      print('[Close] >> Fail')

  

  @timer
  def _extract(self, pool, data):
    try:
      # print("data")
      # print(data)

      # print("data['Response'].tolist()")
      # print(data['Response'].tolist())
      self.papers_text = pool.map(self._json, data['Response'].tolist())
      # print("self.papers_text")
      # print(self.papers_text)

      if self._start:
        print('\n ---')
        print(f"Total Results: {self.papers_text[0]['totalResults']}")
        print(f"Total Pages: {self.papers_text[0]['totalPages']}")
        print(f"Query Suggestions: {self.papers_text[0]['querySuggestions']}")
        print('--- \n')
        self.totalPages = self.papers_text[0]['totalPages']
        self.totalResults = self.papers_text[0]['totalResults']
        self._start = False

      
      print("[_extract] >> extracting relevant data.")
      check_point= [{"Page": {"N_Page":page['query']['page'],
                                   "N_Papers":len(page['results']),
                                   "Papers": pool.map(self._paperExtract,
                                                      page['results'])}} for page in self.papers_text]


      # print(check_point)
      if self.saveFile:
        try:
          self._save(check_point)
        except:
          print("_save >> [Fail] to save.")
          print("_extract>> [Fail], see .badcall to reextract content.")
          self.badcall.append(self.papers_text)
          # print(self.badcall)
      else:
        self.all["Results"].extend(check_point)


    except:
      print("_extract>> [Fail], see .badcall to reextract content.")
      self.badcall.append(self.papers_text)
      print(self.badcall)
    
    

  # def _data(self, data):
  #   if type(self.datasource) == str:
  #     self.datasource = data
  #   else:
  #     self.datasource = pd.concat([self.datasource, data])

  @timer
  def _runtime(self, pool, pages):
    self.totalPages = 0

    find = False
    
    while True:
      if self.saveFile:
        close = self._startFile(find)
      
      print('\n')
      print('[_runtime]>> Start searching...')
      # print(self.totalPages)
      # print(self.totalResults)
      # print(self.n)

      if self.totalResults < self.n:
        self.n = self.totalResults
        pages = list(range(self._page, self.totalPages))
      
      try:
        res = pool.map(self._query, pages)
        # print(res)
        resultData = pd.DataFrame(res, columns=["Response", "Page", "Code"])
        resultData.set_index("Page")
        
        if resultData.query("Code !=200").size == 0:
          # self._data(resultData)
          self._extract(pool, resultData.query("Code ==200"))
          if self.saveFile:
            if close:
              self._endFile()
              find = True
          break
        else:
          find = False

          if resultData.query("Code ==200").size != 0:
            self._extract(pool, resultData.query("Code ==200"))
            if self.saveFile:
              if close:
                find = True
                self._endFile()
              
          print("Bad call of pages:")
          # self._data(resultData.query("Code == 200"))
          # self.datasource.append(resultData.query("Code ==200"))
          pages = resultData.query("Code !=200")["Page"].values.tolist()
          print(pages)
          try:
            with open("./BadCalls.text", 'w', encoding='UTF-8') as fp:
              fp.write(str(pages))
          except:
            print("Fail to save badcalls")
          print(f"Tentando de novo daqui a {self.sleeptry/60} min...")


          sleep(self.sleeptry)
      except:
        pass
      print("---")
        
        
    
    
    # self._extract(pool, self.datasource)


  @timer
  def get(self, n = 10, page = 1, pages = []):
    self._pages = pages
    self.n = n
    self._page = page
    self.totalResults = 1000000000000000000000
    self.post["pageSize"] = 10
    self.post["page"] = page
    self.all = {"Results": []}
    print('.post >>')
    print(self.post)
    # self.datasource = ''
    print("\n")
    print("Searching...")
    print(self.all)

    

    with mp.Pool(self.poolCPU) as pool:
      if self.n > 10:
    
        if len(pages) != 0:
          self._pages = pages
        else:  
          self._pages = list(range(self._page, (self.n//10)+self._page))
      # for page in range(n//10):
        self._runtime(pool, self._pages)
          
        if n%10>0:
          self._pages = [self.n//10+self._page]
          self.post["pageSize"] = self.n%10

          self._runtime(pool, self._pages)
          
      else:
        # pass
        self._pages = [self._page]
        self.post["page"] = self._page
        self.post["pageSize"] = self.n

        self._runtime(pool, self._pages)

    
      # self._extract(pool, self.datasource)


##### Description #####
# ex. {"params": value} 
#  
##### Params that can pass in SearchWeb().get(params = value): #####
#     {
#     "n": 1000 (how much papers)
#     "page": 1, (where start search)
#      }
##### Params that can pass in SearchWeb(params = value): #####
# data = '''{
#     "Savename": 'Data'
#     "sleeptry": 3 (seconds)
#     "poolCPU": 4 (Number of clusters, CPU)
#     "save": False
#     "queryString": "Machine Learning+Deep Learning",
#     "sort": "total-citations", #influence #"pub-date" #relevance
#     "authors": [],
#     "coAuthors": [],
#     "venues": [
#         "PloS one",
#         "AAAI",
#         "Scientific reports",
#         "IEEE Access",
#         "ArXiv",
#         "Expert Syst. Appl.",
#         "ICML",
#         "Neurocomputing",
#         "Sensors",
#         "Remote. Sens."
#     ],
#     "yearFilter": {
#         "min": 2008,
#         "max": 2021
#     },
#     "requireViewablePdf": True,
#     "publicationTypes": [
#         "ClinicalTrial",
#         "CaseReport",
#         "Editorial",
#         "Study",
#         "Book",
#         "News",
#         "Review",
#         "Conference",
#         "LettersAndComments",
#         "JournalArticle"
#     ],
#     "externalContentTypes": [],
#     "fieldsOfStudy": [
#         "biology",
#         "art",
#         "business",
#         "computer-science",
#         "chemistry",
#         "economics",
#         "engineering",
#         "environmental-science",
#         "geography",
#         "geology",
#         "history",
#         "materials-science",
#         "mathematics",
#         "medicine",
#         "philosophy",
#         "physics",
#         "political-science",
#         "psychology",
#         "sociology"
#     ],
#     "useFallbackRankerService": False,
#     "useFallbackSearchCluster": False,
#     "hydrateWithDdb": True,
#     "includeTldrs": True,
#     "performTitleMatch": True,
#     "includeBadges": True,
#     "tldrModelVersion": "v2.0.0",
#     "getQuerySuggestions": False
# }
# '''
# '''
# Obs. Params that have a list can be a empty list
# Ex. {"venues": []}

### Discoment here to have a script
if __name__ == '__main__':
  SearchWeb(
    search= "decision making+optimization+artificial intelligence",
    sort= "influence",
    Savename = "influence_data",
    save=True,
    poolCPU = 4,
    sleeptry = 3.5*60,
    venues = [],
    publicationTypes = ['JournalArticle'],
    fieldsOfStudy = [],
    getQuerySuggestions = True
    ).get(20000, page = 1)
