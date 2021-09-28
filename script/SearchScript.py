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





class SearchAPI():
  def __init__(self, search="decision making+optimization+artificial intelligence", poolCPU = 4, sleeptry=5, save = False, **kwargs):
     
    self.total = 0
    self.sleeptry = sleeptry
    self.poolCPU = poolCPU
    self.saveName = kwargs.get('Savename', "Data")

    self.badcall = []

    self.saveFile = save

    self._api = "https://api.semanticscholar.org/graph/v1/paper/search"

    self.params = {
    "query": search, 
    "limit": 100,
    "fields": kwargs.get('fields', "title,abstract,isOpenAccess,fieldsOfStudy"),
    "offset": kwargs.get('offset', 0),
    }



  def _query(self, offset):
    # print("_query")
    params = self.params.copy()
    if offset + params['limit'] >= 10000:
      params['limit'] = 10000 - offset - 1
      params['offset'] = offset
    else:
      params['offset'] = offset
    # post["page"] = page
    # print(params)
    try:
      # &
      url = self._api +"?query=" + str(params['query']) + "&limit=" + str(params['limit']) + "&fields=" + str(params['fields']) + "&offset=" +  str(params['offset'])
      # print(url)
      res = requests.get(url, timeout=15)
      # sleep(self.sleeptry)
      # print(res)
      res.encoding = 'utf-8'
      return [res, offset, res.status_code]
    except:
      return [None, offset, 400 ]

  def _pandas(self, res):
    dict_data = json.loads(res.text)
    # print(len(dict_data['data']))

    self.total= self.total+ len(dict_data['data'])
    return pd.DataFrame(dict_data['data'])

  def save(self, name, data):
    # csvFile = Path(f"./{name}.csv")
    
    # if csvFile.is_file():
    #   x = pd.read_csv(f'{name}.csv')
    #   data = pd.concat([data,x])

    try:
      data.to_csv(f'{name}.csv')
    except:
      print("[Save]>> Error to save the data.")



  @timer
  def _extract(self, pool, data):
    try:
      papers_list = pool.map(self._pandas, data['Response'].tolist())

      self.all.extend(papers_list)

      if self.saveFile:
        self.save(self.saveName ,pd.concat(self.all).reset_index())

    except:
      print("_extract>> [Fail], see .badcall to reextract content.")
      # self.badcall.append(self.papers_text)
      # print(self.badcall)
   
      


  @timer
  def _runtime(self, pool, offsets):
    # self.totalPages = 0

    # find = False
    
    while True:
      # if self.saveFile:
      #   close = self._startFile(find)
      
      print('\n')
      print('[_runtime]>> Start searching...')

      try:
        res = pool.map(self._query, offsets)
        resultData = pd.DataFrame(res, columns=["Response", "Page", "Code"])
        # print(resultData["Code"])

        resultData.set_index("Page")
        
        if resultData.query("Code !=200").size == 0:
          self._extract(pool, resultData.query("Code ==200"))

          break
        else:

          if resultData.query("Code ==200").size != 0:
            self._extract(pool, resultData.query("Code ==200"))
              
          print("Bad call of pages:")
          # self._data(resultData.query("Code == 200"))
          # self.datasource.append(resultData.query("Code ==200"))
          offsets = resultData.query("Code !=200")["Page"].values.tolist()
          print(offsets)
          err = resultData.query("Code !=200")["Response"].tolist()
          err = [x.text for x in err]
          print('Erros: ')
          print(err)
          try:
            with open("./BadCalls.text", 'w', encoding='UTF-8') as fp:
              fp.write(str(offsets))
          except:
            print("Fail to save badcalls")
          print(f"Tentando de novo daqui a {self.sleeptry/60} min...")


          sleep(self.sleeptry)
      except:
        pass
      print("---")

        
        
    
    
    # self._extract(pool, self.datasource)


  @timer
  def get(self, n = 10, offset = 0, papers = []):
    self.n = 10000 if n > 10000 else n
    print(self.n)
    self._offset = offset
    # self.post["pageSize"] = 10
    # self.post["page"] = page
    self.all = []
    # print('.post >>')
    # print(self.post)
    # self.datasource = ''
    print("\n")
    print("Searching...")


    

    with mp.Pool(self.poolCPU) as pool:
      if self.n > 100:
    
        if len(papers) != 0:
          self._offsets = papers
        else:
          self._offsets = list(range(self._offset, (self.n//100)+self._offset))
          lista = [x*100 for x in self._offsets]
          # lista.insert(0,self._offsets[0])
          # print(lista)
          offsets = lista
          
          print("offsets: ")
          print(offsets)
        
        # print(self._offsets)
      # for page in range(n//10):
        self._runtime(pool, offsets)
          
        if n%100>0:
          self.params['limit'] = n%100
          self._offsets = [lista[-1] + 100]
          # print(self.params)
          # print(self._offsets)

          self._runtime(pool, self._offsets)
          
      else:
        # pass
        if len(papers) != 0:
          self._offsets = papers
        else:  
          offsets = [self._offset]
        
        self.params['limit'] = n
        self._runtime(pool, offsets)

    self.all = pd.concat(self.all, ignore_index=True)



if __name__ == '__main__':
  SearchAPI(
    search="decision making+optimization+artificial intelligence",
    fields='paperId,externalIds,url,title,abstract,venue,year,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy,authors',
    sleeptry = 1*20, # seconds
    save=True,
    Savename = "dataAPI").get(11000)

