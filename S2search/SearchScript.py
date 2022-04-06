import requests
import json
import multiprocessing as mp
import pandas as pd
from time import sleep, time
import os

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

class S2paperAPI():
  """
  Description
  ~~~~~~~~~~~~~~~~~~~~~
    Class that when instantiate in a variable consumes the api
    of Semantic Scholar API about the papers.
    
  Parameters
  ~~~~~~~~~~~~~~~~~~~~~
  
  `SearchAPI(poolCPU = 4, sleeptry = 5)`:
    - `poolCPU : (int)` |
      Number of cores of CPU to make multiples request in the same time.
    - `sleeptry : (float)` |
      Seconds to wait for try again when Semantic Scholar block the requests.
  
  Example
  ~~~~~~~~~~~~~~~~~~~~~
  
   >>> from S2search import S2paperAPI
   >>> m = S2paperAPI()
   >>> m.get("artificial intelligence", n=2)
   >>> m.all.shape
   (2, 12)
   >>> m.all['title']
   0    Explainable Artificial Intelligence (XAI): Con...
   1    Explanation in Artificial Intelligence: Insigh...
   Name: title, dtype: object

"""
  def __init__(self, poolCPU=4, sleeptry=5):
    self.sleeptry = sleeptry
    self.poolCPU = poolCPU
    self.badcalls = []
    self._api = "https://api.semanticscholar.org/graph/v1/paper/search"
   
 
  # The main Function to get the papers.
  @timer
  def get(self, search="artificial intelligence", n=10, offset=0, papers=[], save=False, **kwargs):
    """
    .get()
    ~~~~~~~~~~~~~~~~~~~~~
    
    `SearchAPI().get(search, n = 10, offset = 0, papers = [], save = False, saveName = Data, fields = ["title","abstract","isOpenAccess","fieldsOfStudy"])`
    
    Parameters
    ~~~~~~~~~~~~~~~~~~~~~
    
    - `search : (str)` |
          The main query in Semantic Scholar API about the papers.
    - `n : (int)` |
          The number of papers to get, the maximum is 10.000.
    - `offset : (int)` |
          Where start to return the papers, the default is 0,
          that is the first paper found.
    - `papers : list(int)` |
          A list of positions of the papers (0 is the first one), if pass a list, the parameters (n, offset)
          have no effect in the main query (search). The default is a empty list [].
    - `save : (bool)` |
          If true, will save the data set in a file csv at the current directory. the default is False.
    - `saveName : (str)` |
          The name of the file when the save is set True.
    - `fields : list(str)` |
          The dataframe columns that the Semantic Scholar API returns, see the documentation in <https://api.semanticscholar.org/graph/v1#operation/get_graph_get_paper_search>.
    
    Returns
    ~~~~~~~~~~~~~~~~~~~~~
    
        When the parameter (save) is False, the data set found will be in the (.all) variable as pandas
        Dataframe of the class instantiated.
    """
    
    self.saveName = kwargs.get('saveName', "Data")
    self.saveFile = save
    self._offset = offset
    self.all = []
    """
    A dataFrame with all content as pandas DataFrame.
    """
    self.n = 10000 if n > 10000 else n
    """
    Number of papers.
    """

    self.params = {
    "query": search,
    "limit": 100,
    "fields": ",".join(kwargs.get('fields', ["paperId",
                                             "title",
                                             "abstract",
                                             "isOpenAccess",
                                             "fieldsOfStudy",
                                             "url",
                                             "venue", 
                                             "year", 
                                             "referenceCount",
                                             "citationCount",
                                             "influentialCitationCount",
                                             "authors"])),
    "offset": kwargs.get('offset', 0),
    }

    if len(papers) != 0:
          self._offsets = papers
          offsets = papers
          self.params['limit'] = 1
          self.n = len(papers)
    else:
          inf = self._offset//100
          sup = (self.n)//100+self._offset//100

          if inf == sup:
            self._offsets = [inf]
          else:
            self._offsets = list(range(inf, sup))
          self.params['limit'] = 100
          offsets = [x*100 for x in self._offsets if x*100 < 10000]
    
    print("\n")
    print("Searching...")
    print("offsets: ")
    print(offsets)

    with mp.Pool(self.poolCPU) as pool:
      if self.n > 100:
            
        self._runtime(pool, offsets)
        
        if len(papers) == 0:
          if n%100>0:
            self.params['limit'] = n%100
            offsets = [offsets[-1] + 100]

            self._runtime(pool, offsets)
          
          
      else:
        if len(papers) == 0:  
          offsets = self._offsets
          self.params['limit'] = n
        
        self._runtime(pool, offsets)
      
    self.all = pd.concat(self.all, ignore_index=True)
    """
    A dataFrame with all content as pandas DataFrame
    """

    if self.saveFile:
      words = os.path.join(os.getcwd(), f'{self.saveName}')
      print(f"[Save]>> Saved in {words}.csv")


# The main function called in get to execute a script to get the papers.
  @timer
  def _runtime(self, pool, offsets):
    while True:
      print('\n')
      print('[_runtime]>> Start searching...')

      try:
        res = pool.map(self._query, offsets)
        
        resultData = pd.DataFrame(res, columns=["Response", "Page", "Code"])
        resultData.set_index("Page")
        
        if resultData.query("Code !=200").size == 0:
          self._extract(pool, resultData.query("Code ==200"))
          

          break
        
        else:
          if resultData.query("Code ==200").size != 0:
            self._extract(pool, resultData.query("Code ==200"))
              
          print("Bad call of pages:")
          offsets = resultData.query("Code !=200")["Page"].values.tolist()

          print(offsets)
          
          err = resultData.query("Code !=200")["Response"].tolist()
          err = [x.text for x in err]
          print('Errors: ')
          print(err)
          
          if self.saveFile:
            try:
              with open("./BadCalls.text", 'w', encoding='UTF-8') as fp:
                fp.write(str(offsets))
            except Exception:
              print("Fail to save badcalls.")
          else:
            self.badcalls = offsets
            
          print(f"Trying again in {round(self.sleeptry/60, 2)} min...")
          sleep(self.sleeptry)
          
      except Exception:
        print("[_runtime]>> Error... Trying again.")
        pass
      print("---")

  # Function to extract the content of the response and save with all that have success.
  @timer
  def _extract(self, pool, data):
    try:
      papers_list = pool.map(self._pandas, data['Response'].tolist())

      self.all.extend(papers_list)

    except Exception as error:
      print("_extract>> [Fail], see .badcall to reextract content.")
      raise error
    
    if self.saveFile:
      self.save(self.saveName , pd.concat(self.all).reset_index())
      
# Function that make requisitions on the API of Semantic Scholar.
  def _query(self, offset):
    params = self.params.copy()
    if offset + params['limit'] >= 10000:
      params['limit'] = 10000 - offset - 1
      params['offset'] = offset
    else:
      params['offset'] = offset
    try:
      url = self._api +"?query=" + str(params['query']) + "&limit=" + str(params['limit']) + "&fields=" + str(params['fields']) + "&offset=" +  str(params['offset'])
      res = requests.get(url, timeout=15)
      res.encoding = 'utf-8'
      return [res, offset, res.status_code]
    except Exception:
      return [None, offset, 400 ]

# Function that treat the response of the API and return a pandas Dataframe.
  def _pandas(self, res):
    dict_data = json.loads(res.text)
    return pd.DataFrame(dict_data['data'])

# Function to save the data
  def save(self, name, data):
    try:
      data.to_csv(os.path.join(os.getcwd(), f'{name}.csv'))
    except Exception as error:
      words = os.path.join(os.getcwd(), f'{name}.csv')
      print(f"[Save]>> Error to save the data in {words}")
      raise error
