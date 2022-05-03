# How to install

```python
pip install S2query
```
# S2query

Sematic Scholar paper search developed by BecomeAllan (c) 2020 is library that can search papers on [Semantic Scholar page](https://www.semanticscholar.org/) or in the [API](https://api.semanticscholar.org/graph/v1) provided by them.

S2query is an request http library, written in Python, to retrieve papers available in Semantic Scholar.

# Examples

We have two main classes, that can handle the paper data. To make a query about more than one topic, title, etc... The parameter `search`, have to be a string like:

to add some, use `+`:

+ `search = "artificial intelligence+Deep Learning"`

or if you want to exclude some, use the `-` to exclude:

+ `search = "artificial intelligence-application"`
  
## S2paperAPI()

The `S2paperAPI()`, consume the API of Semantic Scholar. See the [Link](https://api.semanticscholar.org/graph/v1) to understand more about the API.

The return in `.all` is a Pandas [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

```python
   >>> from S2query import S2paperAPI
   >>> m = S2paperAPI()
   >>> m.get("artificial intelligence", n=2)
   >>> m.all.shape
   (2, 12)
   >>> m.all['title']
   0    Explainable Artificial Intelligence (XAI): Con...
   1    Explanation in Artificial Intelligence: Insigh...
   Name: title, dtype: object
```

## S2paperWeb()

The `S2paperWeb()`, consume the content in the [page](https://www.semanticscholar.org/) in Semantic Scholar.

The return in `.all` is a dictionary arranged about the pages founded.

```python
   >>> from S2query import S2paperWeb
   >>> m = S2paperWeb()
   >>> m.get("artificial intelligence+Deep Learning", n=3, sort = "total-citations", fieldsOfStudy = ['biology'])
   >>> len(m.all['Results'][0]['Page']['Papers'])
   3
   >>> m.all['Results'][0]['Page']['Papers'][0].keys()
   dict_keys(['authors', 'id', 'socialLinks', 'title', 'paperAbstract', 'year',
    'venue', 'citationContexts', 'citationStats', 'sources', 'externalContentStats',
    'journal', 'presentationUrls', 'links', 'primaryPaperLink', 'alternatePaperLinks',
    'entities', 'entityRelations', 'blogs', 'videos', 'githubReferences',
    'scorecardStats', 'fieldsOfStudy', 'pubDate', 'pubUpdateDate',
    'badges', 'tldr'])
```

# Parameters

These classes have an optimization with CPU cores that make multiple requests at the same time, which is passed as a parameter like the number of cores pass as parameter `poolCPU`. Because of this fact, the Semantic Scholar server may stop receiving requests for a while, so we have defined a timeout in seconds so that we can continue these requests, the parameter is `sleeptry`.


## Example

```python
   >>> from S2query import S2paperWeb, S2paperAPI
   >>> m = S2paperWeb(poolCPU = 2, sleeptry = 60)
   >>> k = S2paperAPI(poolCPU = 4, sleeptry = 5)
```

To more specific search, this classes have a main function `.get()` with can hame some parameters that can help.

+ `S2paperAPI().get(search, n = 10, offset = 0, papers = [], save = False, saveName = Data, fields = ["title","abstract","isOpenAccess","fieldsOfStudy"])`

    - Parameters:
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
          The dataframe columns that the Semantic Scholar API returns, see the documentation in [Semantic Scholar API Doc.](https://api.semanticscholar.org/graph/v1#operation/get_graph_get_paper_search).


+ `S2paperWeb().get(search, n = 10, offset = 0, papers = [], save = False, saveName = Data, **kwargs)`
    - Parameters:
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
          The filter of fields of study, the options are `[ "agricultural-and-food-sciences","art","biology","business","computer-science","chemistry","economics","education","engineering","environmental-science","geography","geology","history","law","linguistics","materials-science","mathematics","medicine","philosophy","physics","political-science","sociology","psychology"]`. The default is `[]`.
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
