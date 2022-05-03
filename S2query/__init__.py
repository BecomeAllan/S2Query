"""
(S2search) Sematic Scholar paper search
~~~~~~~~~~~~~~~~~~~~~

S2search is an request http library, written in Python, to retrieve papers available in Semantic Scholar.

Basic usage:

We have two main classes, that can handle the paper data:

S2paperAPI()
~~~~~~~~~~~~~~~~~~~~~

Search paper using the data provided by Seamantic Scholar API papers: <https://api.semanticscholar.org/graph/v1>.

   >>> from S2search import S2paperAPI
   >>> m = S2paperAPI()
   >>> m.get("artificial intelligence", n=2)
   >>> m.all.shape
   (2, 12)
   >>> m.all['title']
   0    Explainable Artificial Intelligence (XAI): Con...
   1    Explanation in Artificial Intelligence: Insigh...
   Name: title, dtype: object

S2paperWeb()
~~~~~~~~~~~~~~~~~~~~~

Search paper using the data provided by the page of Semantic Scholar: <https://www.semanticscholar.org>.

   >>> from S2search import S2paperWeb
   >>> m = S2paperWeb()
   >>> m.get("artificial intelligence+Deep Learning", n=3, sort = "total-citations", fieldsOfStudy = ['biology'])
   >>> len(m.all['Results'][0]['Page']['Papers'])
   3
   >>> m.all['Results'][0]['Page']['Papers'][0].keys()
   dict_keys(['authors', 'id', 'socialLinks', 'title', 'paperAbstract', 'year', 'venue', 'citationContexts', 'citationStats', 'sources', 'externalContentStats', 'journal', 'presentationUrls', 'links', 'primaryPaperLink', 'alternatePaperLinks', 'entities', 'entityRelations', 'blogs', 'videos', 'githubReferences', 'scorecardStats', 'fieldsOfStudy', 'pubDate', 'pubUpdateDate', 'badges', 'tldr'])

:license: MIT 2.0, see LICENSE for more details.
"""

__docformat__ = "restructuredtext"

# Let users know if they're missing any of our hard dependencies
hard_dependencies = ("requests", "json", "multiprocessing", "pandas", "time", "os", "ast", "re", "pathlib")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies


from .SearchScript import S2paperAPI
from .SearchWebScript import S2paperWeb

