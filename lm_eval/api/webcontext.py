import re
import string
import requests
import aiohttp
import asyncio
import datasets
from tqdm import tqdm
from lm_eval.api.excluded_domains import excluded_domains
import re
import string
import math

class webcontext():

    def __init__(self) -> None:

        self.contaminatedWebContext = 0
        self.contaminatedUrls = []
        self.GoodUrls = []
        self.questionWithoutContext = []
        self.noContext = 0
        self.contaminatedQueries = 0
        self.semaphore = asyncio.Semaphore(2)
        self.key = ""


    def clearText(self,text):
        text = text.lower()
        patterns = [
            r'^[A-Za-z]{3} \d{1,2}, \d{4} —\s*', # np. "Oct 7, 2024 — "
            r'^\d{1,2} [a-z]{3} \d{4} —\s*',      # np. "1 sie 2024 —"
            r'^by [A-Za-z ]+ · \d{4} · cited by \d+ —\s*', # np. "by John Doe · 2024 · Cited by 10 —"
            r'^[A-Za-z ]+ · \d{4} · cytowane przez \d+ —\s*',  # np. "Broda· 1967 · Cytowane przez 832 —"
            r'^[A-Za-z ]+ cytowane przez \d+\s*',  # np. "e blacksher cytowane przez 6"
            r'^[A-Za-z ]+ cited by \d+\s*',  # np. "e blacksher cytowane przez 6"
            r'^[A-Za-z ]+ · \d{4} —\s*', # np. "John Doe · 2024 —"
            r'^by [A-Za-z ]+ —\s*', # np. "by John Doe —"
            r'^\d{1,2} [a-zA-Z]+ ago —\s*', # np. "1 day ago —"
        ]

        for pattern in patterns:
            text = re.sub(pattern, '', text)

        text = text.translate(str.maketrans('', '', string.punctuation + "–_·"))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def getNgrams(self, text, n=2):
        words = text.split()
        if len(words) < n:
            return []
        
        return [words[i:i+n] for i in range(len(words) - n + 1)]

    def getSimilarNgramsNum(self, question, webText):
        i = 0
        for ngram in webText:
            if ngram in question:
                i += 1
        return i

    def isNotContaminated(self, question, webContext):
        question = self.clearText(question)
        webContext = self.clearText(webContext)

        q_ngrams= self.getNgrams(question)
        web_ngrams = self.getNgrams(webContext)

        if not q_ngrams or not web_ngrams:
            return True, question, webContext

        similar_ngrams = self.getSimilarNgramsNum(q_ngrams, web_ngrams)

        if len(q_ngrams) > len(web_ngrams):
            if webContext in question:
                return False, question, webContext
            
            if similar_ngrams < math.ceil(len(web_ngrams) / 2):
                return True, question, webContext
            else:
                return False, question, webContext

        elif len(q_ngrams) < 5:
            if similar_ngrams <= len(q_ngrams) + 1:
                return True, question, webContext
            else:
                return False, question, webContext

        else:
            if similar_ngrams < math.ceil(len(q_ngrams) / 2): 
                return True, question, webContext
            else:
                return False, question, webContext


    async def fetch(self, session, query):
        try:
            async with self.semaphore: 
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
            try:

                results = await self.fetch(session, query)

                if not results or results is None or "results" not in results:
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
                        notconaminated, question, webContext = self.isNotContaminated(query, result["content"])
                        if result["parsed_url"][1].endswith("wikipedia.org") or notconaminated:
                            doc['WebContext'] = webContext
                            self.GoodUrls.append({"query": question, "content": webContext, "url": result["url"]})
                            return doc
                        
                        else:
                        
                            self.contaminatedUrls.append({"query": question, "content": webContext, "url": result["url"]})
                            self.contaminatedWebContext += 1
                            if firstIteration:
                                self.contaminatedQueries += 1
                                firstIteration = False
                            
                self.noContext += 1
                doc['WebContext'] = "None"
                self.questionWithoutContext.append(query)
                return doc
            
            except Exception as e:
                print(f"\nQ: {query} get_web_context_async Err: {str(e)}")
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
        try:
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
        except Exception as e:
            print(f"GetMatchingQuestionKey Error: {str(e)}")
            self.key = None
            return