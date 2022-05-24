import requests
import json
import multiprocessing as mp
import os
import pandas as pd
import re
import ast
from pathlib import Path


from time import sleep, time


# (Decorantor)
# - Description:
#     Function that times the execution of other functions
# - Return:
#     Print the time consuming of a function
#
def timer(fun):
  def warper(*args, **kwargs):
    start = time()
    d = fun(*args, **kwargs)
    end = time()
    print(f"[{fun.__name__}]>> Took {round(end-start,2)}s")
    return d
  return warper




class S2paperWeb():
  """
  Description
  ~~~~~~~~~~~~~~~~~~~~~
  
    Class that when instantiate in a variable consumes the content
    of Semantic Scholar webpage about the papers.
    
  Parameters
  ~~~~~~~~~~~~~~~~~~~~~

  `S2paperWeb(poolCPU = 4, sleeptry = 5)`:
    - `poolCPU : (int)` |
          Number of cores of CPU to make multiples request in the same time.
    - `sleeptry : (float)` |
          Seconds to wait for try again when Semantic Scholar block the requests.

  Example
  ~~~~~~~~~~~~~~~~~~~~~

   >>> from S2search import S2paperWeb
   >>> m = S2paperWeb()
   >>> m.get("artificial intelligence+Deep Learning", n=3, sort = "total-citations", fieldsOfStudy = ['biology'])
   >>> len(m.all['Results'][0]['Page']['Papers'])
   3
   >>> m.all['Results'][0]['Page']['Papers'][0].keys()
   dict_keys(['authors', 'id', 'socialLinks', 'title', 'paperAbstract', 'year', 'venue', 'citationContexts', 'citationStats', 'sources', 'externalContentStats', 'journal', 'presentationUrls', 'links', 'primaryPaperLink', 'alternatePaperLinks', 'entities', 'entityRelations', 'blogs', 'videos', 'githubReferences', 'scorecardStats', 'fieldsOfStudy', 'pubDate', 'pubUpdateDate', 'badges', 'tldr'])

"""
  def __init__(self, poolCPU = 4, sleeptry=5):
    self.post = {}
    self.sleeptry = sleeptry
    self.poolCPU = poolCPU
    self.badcall = []
    self._start = True
    self._url = "https://www.semanticscholar.org/api/1/search"
    
  
  # The main Function to get the papers.
  @timer
  def get(self, search="Machine Learning+Deep Learning", n = 10, page = 1, pages = [], save = False, **kwargs):
    """
    .get()
    ~~~~~~~~~~~~~~~~~~~~~
    
    `S2paperWeb().get(search, n = 10, offset = 0, papers = [], save = False, saveName = Data)`
    
    Parameters
    ~~~~~~~~~~~~~~~~~~~~~
    - `search : (str)` |
          The main query in Semantic Scholar API about the papers.
    - `n : (int)` |
          The number of papers to get.
    - `save : (bool)` |
          If true, will save the data set in a file csv at the current directory. the default is False.
    - `saveName : (str)` |
          The name of the file when the save is set True.
    - `page : (int)` |
          Where start to return of the papers, the default is 1, that is the first paper found.
    - `sort : (str)` |
          The order of the return paper, the options are `("total-citations", "influence", "pub-date", "relevance")`.
          The default is "relevance".
    - `authors : list(str)` |
          The filter of authors. The default is `[]`.
    - `coAuthors : list(str)` |
          The filter of cothors. The default is `[]`.
    - `venues : list(str)` |
          The filter of venues. The options are `["PloS one", "AAAI", "Scientific reports", "IEEE Access", "ArXiv",
          "Expert Syst. Appl.""ICML", "Neurocomputing", "Sensors", "Remote. Sens."]`. The default is `[]`.
    - `yearFilter : dict({"min": int, "max": int})` |
          The filter of year. Ex. `{"min": 1999, "max": 2021}`. The default is `None`.
    - `requireViewablePdf : (bool)` |
          If the paper have pdf.
    - `publicationTypes : list(str)` |
          The filter of type publication, the options are `["ClinicalTrial","CaseReport","Editorial","Study",
          "Book","News","Review","Conference","LettersAndComments","JournalArticle"]`. The default is `[]`
    - `fieldsOfStudy : list(str)` |
          The filter of fields of study, the options are `["biology","art","business",
          "computer-science","chemistry","economics","engineering","environmental-science",
          "geography","geology","history","materials-science","mathematics","medicine","philosophy",
          "physics","political-science","psychology","sociology"]`. The default is `[]`.
    - `useFallbackRankerService : (bool)` |
          Fall back to rank the match papers. The defalt is `False`.
    - `useFallbackSearchCluster : (bool)` |
          Fall back to cluster the match papers. The defalt is `False`.
    - `hydrateWithDdb : (bool)` |
          The defalt is `True`.
    - `includeTldrs : (bool)` |
          AI based summary abstracts of papers. The defalt is `True`.
    - `"tldrModelVersion" : (str)` |
          The AI version. The default is `"v2.0.0"`
    - `performTitleMatch: (bool)` |
          Match papers about title. The defalt is `True`.
    - `includeBadges: (bool)` |
          Some bagdes about the papers. The defalt is `True`.
    - `getQuerySuggestions: (bool)` |
          Some query suggestions. The defalt is `True`.
    - `papers : list(int)` |
          A list of positions of the papers (0 is the first one), if pass a list, the parameters (n, offset)
          have no effect in the main query (search). The default is a empty list [].
    
    Returns
    ~~~~~~~~~~~~~~~~~~~~~
        When the parameter (save) is False, the data set found will be in the (.all) variable as a dictionary
        in the class instantiated.
    """
    
    self.saveName = kwargs.get('saveName', "Data")

    self.saveFile = save
    self._search = search
    
    self._sort = kwargs.get('sort', "relevance")
    self._authors = kwargs.get('authors', [])
    self._coAuthors = kwargs.get('coAuthors', [])
    self._venues = kwargs.get('venues', [])
    self._yearFilter = kwargs.get('yearFilter', None) 
    self._requireViewablePdf = kwargs.get('requireViewablePdf', False)
    self._publicationTypes = kwargs.get('publicationTypes', [])
    self._fieldsOfStudy = kwargs.get('fieldsOfStudy', [])
    self._useFallbackRankerService = kwargs.get('useFallbackRankerService', False)
    self._useFallbackSearchCluster = kwargs.get('useFallbackSearchCluster', False)
    self._hydrateWithDdb = kwargs.get('hydrateWithDdb', True)
    self._includeTldrs = kwargs.get('includeTldrs', True)
    self._performTitleMatch = kwargs.get('performTitleMatch', True)
    self._includeBadges = kwargs.get('includeBadges', True)
    self._tldrModelVersion = kwargs.get('tldrModelVersion', 'v2.0.0')
    self._getQuerySuggestions = kwargs.get('getQuerySuggestions', True)
    
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
    "fieldsOfStudy": [x.lower() for x in self._fieldsOfStudy],
    "useFallbackRankerService": self._useFallbackRankerService,
    "useFallbackSearchCluster": self._useFallbackSearchCluster,
    "hydrateWithDdb": self._hydrateWithDdb,
    "includeTldrs": self._includeTldrs,
    "performTitleMatch": self._performTitleMatch,
    "includeBadges": self._includeBadges,
    "tldrModelVersion": self._tldrModelVersion,
    "getQuerySuggestions": self._getQuerySuggestions,
     "useS2FosFields": True
    }
    
    self._pages = pages
    self.n = n
    self._page = page
    self.totalResults = 1000000000000000000000
    self.post["pageSize"] = 10
    self.post["page"] = page
    self.all = {"Results": []}
    
    # print('.post >>')
    # print(self.post)
    print("\n")
    print("Searching...")

    with mp.Pool(self.poolCPU) as pool:
      if self.n > 10:
    
        if len(pages) != 0:
          self._pages = pages
        else:  
          self._pages = list(range(self._page, (self.n//10)+self._page))
        self._runtime(pool, self._pages)
          
        if n%10>0:
          self._pages = [self.n//10+self._page]
          self.post["pageSize"] = self.n%10

          self._runtime(pool, self._pages)
          
      else:
        self._pages = [self._page]
        self.post["page"] = self._page
        self.post["pageSize"] = self.n

        self._runtime(pool, self._pages)
        
    if self.saveFile:
        words = os.path.join(os.getcwd(), f'{self.saveName}')
        print(f"[Save]>> Saved in {words}.json")

# The main function called in get to execute a script to get the papers.
  @timer
  def _runtime(self, pool, pages):
    self.totalPages = 0

    find = False
    closed = False
    
    while True:
      if self.saveFile:
        close = self._startFile(find)
      
      print('\n')
      print('[_runtime]>> Start searching...')


      if self.totalResults < self.n:
        self.n = self.totalResults
        pages = list(range(self._page, self.totalPages))
      
      try:
        res = pool.map(self._query, pages)
        
        resultData = pd.DataFrame(res, columns=["Response", "Page", "Code"])
        resultData.set_index("Page")
        
        if resultData.query("Code !=200").size == 0:
          self._extract(pool, resultData.query("Code ==200"))
          
          if self.saveFile:
            if close:
              while not(closed):
                closed = self._endFile()
                find = True
          break
        
        else:
          find = False

          if resultData.query("Code ==200").size != 0:
            self._extract(pool, resultData.query("Code ==200"))
            
            if self.saveFile:
              if close:
                while not(closed):
                  closed = self._endFile()
                  find = True
              
          print("Bad call of pages:")
          pages = resultData.query("Code !=200")["Page"].values.tolist()
          print(pages)

          
          err = resultData.query("Code !=200")["Response"].tolist()
          err = [eval(x.text) for x in err]
          print('Errors: ')
          print(err)
          
          if self.saveFile:
            try:
              with open("./BadCalls.text", 'w', encoding='UTF-8') as fp:
                fp.write(str(pages))
            except Exception:
              print("Fail to save badcalls.")
          else:
            self.badcalls = pages 
          
          if "Attempted to page beyond available results" in err[0]['error']:
            break

          print(f"Trying again in {round(self.sleeptry/60, 2)} min...")
          sleep(self.sleeptry)

      except Exception:
        print("[_runtime]>> Error... Trying again")
        print(f"Trying again in {round(self.sleeptry/60, 2)} min...")
        sleep(self.sleeptry)
        pass
      print("---")
  
  
  @timer
  def _extract(self, pool, data):
    try:
      self.papers_text = pool.map(self._json, data['Response'].tolist())

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

      if self.saveFile:
        try:
          self._save(check_point)
        except Exception as err:
          print("_save >> [Fail] to save.")
          raise err
      else:
        self.all["Results"].extend(check_point)

    except Exception as err:
      print("_extract>> [Fail], see .badcall to reextract content.")
      self.badcall.append(self.papers_text)
      print(self.badcall)
      raise err
  
  def _query(self, page):
    post = self.post.copy()
    post["page"] = page
    try:
      res = requests.post(self._url, json=post, timeout=15)
      res.encoding = 'utf-8'
      return [res, page, res.status_code]
    except Exception:
      return [None, page, 400 ]
  
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

  def _json(self, res):
    return json.loads(res.text).copy()

  def save(self, name, data):
    """
    Function that can save the dictionary as a json File.
    """
    try:
      with open(f'./{name}.json', 'w',encoding='UTF-8') as fp:
          json.dump(data, fp)
    except Exception as err:
      print("[Save]>> Error to save the data.")
    raise err
  
  def load_json(self, path):
    """
    Function that can load a json File as a dictionary.
    """
    try:
      with open(f'{path}', 'r', encoding='UTF-8') as fp:
          return json.load(fp)
    except Exception as err:
      print("[load_json]>> Error to load json file.")
      print(err)
      raise err
    
  def _startFile(self, find):
    jsonFile = Path(f"./{self.saveName}.json")
    
    if jsonFile.is_file():
      if find:
        try:
          print(f"[_startFile] >> Loading ./{self.saveName}.json")
          with open(f'./{self.saveName}.json', 'r',encoding='UTF-8') as f:
            data = json.load(f)
          print(f"[Create] >> Creating a ./{self.saveName}.text file to save data.")
          with open(f'./{self.saveName}.text', 'w',encoding='UTF-8') as fp:
            fp.write("{\"Results\": [")
        
          self._save(data['Results'])
        except Exception:
          print(f"[_startFile] >> Fail to load ./{self.saveName}.json")
          try:
            with open(f'./{self.saveName}.text', 'w', encoding='UTF-8') as fp:
              fp.write("{\"Results\": [")
          except Exception as err:
            print("[Create] >> Fail")
            raise err
      else:
        return False
    else:
      try:
        print(f"[Create] >> Creating a ./{self.saveName}.text file to save data.")
        with open(f'./{self.saveName}.text', 'w',encoding='UTF-8') as fp:
          fp.write("{\"Results\": [")
      except Exception as err:
        print("[Create] >> Fail")
        raise err
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
      print(f"[Save] >> Saving check_point at current directory, ./{self.saveName}.text")
      

  def _endFile(self):
    try:
      with open(f'./{self.saveName}.text', 'a', encoding='UTF-8') as fp:
        fp.write(']}')
      
      try:
        with open(f'./{self.saveName}.text', 'r', encoding='UTF-8') as fp:
          text = fp.read()
          text_dict = ast.literal_eval(text)
      
        with open(f'./{self.saveName}.json', 'w', encoding='UTF-8') as fp:
          json.dump(text_dict, fp)
        print(f"[Close] >> Closed and save in ./{self.saveName}.json file the data.")
      except Exception as err:
        print(f"[Close] >> Fail to save the data ./{self.saveName}.json file.")
        raise err
      return True
    except Exception as err: 
      print('[Close] >> Fail')
      print(err)
      return False
