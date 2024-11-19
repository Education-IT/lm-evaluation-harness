import re
import string
import requests
import aiohttp
import asyncio
import datasets
from tqdm import tqdm
from lm_eval.api.excluded_domains import excluded_domains
class webcontext():

    def __init__(self) -> None:

        self.contaminatedWebContext = 0
        self.contaminatedUrls = []
        self.GoodUrls = []
        self.questionWithoutContext = []
        self.noContext = 0
        self.contaminatedQueries = 0
        self.semaphore = asyncio.Semaphore(3)
        self.key = ""


    def clearText(self,text):
        text = text.lower().strip().translate(str.maketrans('', '', string.punctuation + "–"))
        return re.sub(r' +', ' ', text)


    def getFourgrams(self, text):
        words = self.clearText(text).split()
        if len(words) < 4:
            return []
        
        return [[words[i], words[i+1], words[i+2],words[i+3]] for i in range(len(words) - 3)]


    def getSimilarFourgramsNum(self,question,webText):
        i = 0
        for ngram in webText:
            if ngram in question:
                i += 1
        return i


    def isNotContaminated(self,question,webContext):
        q_fourgrams = self.getFourgrams(question)
        if q_fourgrams == []:
            return True
        else:
            web_fourgrams = self.getFourgrams(webContext)
            if self.getSimilarFourgramsNum(q_fourgrams,web_fourgrams) < len(q_fourgrams)//2:
                return True
            else:
                return False


    async def fetch(self, session, query):
        try:
            async with self.semaphore:  # Użyj semafora do ograniczenia liczby zapytań
                async with session.get(f"http://localhost:8080/search?q={query}&format=json") as response:
                    return await response.json()
        except Exception as e:
            print(f"\nQ: {query} Err: {str(e)}")
            return None
        

    async def get_web_context_async(self, doc,task):
        
        if self.key == "":
            self.GetMatchingQuestionKey(doc,task)

        if self.key is None:
            doc['WebContext'] = "None"
            return doc
        else: 
            query = doc[self.key]
        
        
        async with aiohttp.ClientSession() as session:
            results = await self.fetch(session, query)
            if not results or "results" not in results:
                self.noContext += 1
                doc['WebContext'] = "None"
                self.questionWithoutContext.append(query)
                return doc

            filtered_results = [
                res for res in results["results"] if res["parsed_url"][1] not in excluded_domains
            ]

            if filtered_results:
                
                firstIteration = True
                
                for result in filtered_results:
                    
                    if result["parsed_url"][1].endswith("wikipedia.org") or self.isNotContaminated(query, result["content"]):
                        doc['WebContext'] = result["content"].replace("...", "")
                        self.GoodUrls.append({"query": query, "content": result["content"], "url": result["url"]})
                        return doc
                    
                    else:
                    
                        self.contaminatedUrls.append({"query": query, "content": result["content"], "url": result["url"]})
                        self.contaminatedWebContext += 1
                        if firstIteration:
                            self.contaminatedQueries += 1
                            firstIteration = False
                        
            self.noContext += 1
            doc['WebContext'] = "None"
            self.questionWithoutContext.append(query)
            return doc

    async def process_all(self,task):
        tasks = [self.get_web_context_async(doc, task) for doc in task.dataset["test"]]
        
        results = []
        for t in tqdm(asyncio.as_completed(tasks), total=len(task.dataset["test"]), desc="Questions", unit="Q"):
            results.append(await t)

        tasks = None
        return datasets.Dataset.from_dict({key: [d[key] for d in results] for key in results[0]})
    
    def GetMatchingQuestionKey(self,doc,task):

        keys_to_check = [
            "query",
            "question",
            "input",
            None
        ]

        if task.question_key is not None:
            keys_to_check.insert(task.question_key)
        
        for key in keys_to_check:
            if key is None:
                query = re.search(r'{{\s*(\w+)\s*[^}]*}}', task.config.doc_to_text)
                query = query.group(1) if query else None
                if query:
                    self.key = query
                    return
                else:
                    self.key = None
                    return
            elif key in doc:
                self.key = key
                return