import re
import string
import aiohttp
import asyncio
import datasets
from tqdm import tqdm
from lm_eval.api.excluded_domains import excludedDomains
import re
import string
import math
from dotenv import load_dotenv
import os


class webcontext():

    def __init__(self) -> None:
        self.contaminatedDomains = []
        self.validSnippetIndexSum = 0 
        self.suspectedDomains = {}
        self.contaminatedWebContext = 0
        self.contaminatedUrls = []
        self.GoodUrls = []
        self.questionWithoutContext = []
        self.noContext = 0
        self.contaminatedQueries = 0
        self.semaphore = asyncio.Semaphore(1)
        self.key = ""
        load_dotenv()
        self.api_key = os.getenv("API_KEY")




    def clearText(self,text):
        text = text.lower()
        patterns = [
            r'^[A-Za-z]{3} \d{1,2}, \d{4} —\s*',  # np. "Oct 7, 2024 — "
            r'^\d{1,2} [\w]+ \d{4} —\s*',  # np. "25 paź 2024 —"
            r'^by [A-Za-z ]+ · \d{4} · cited by \d+ —\s*',  # np. "by John Doe · 2024 · Cited by 10 —"
            r'^[A-Za-z ]+ · \d{4} · cytowane przez \d+ —\s*',  # np. "Broda· 1967 · Cytowane przez 832 —"
            r'^[A-Za-z ]+ cytowane przez \d+\s*',  # np. "e blacksher cytowane przez 6"
            r'^[A-Za-z ]+ cited by \d+\s*',  # np. "e blacksher cited by 6"
            r'^[A-Za-z ]+ · \d{4} —\s*',  # np. "John Doe · 2024 —"
            r'by [A-Za-z ]+ —\s*',  # np. "by John Doe —"
            r'\d{1,2} [\w]+ ago —\s*',  # np. "1 day ago —"
            r'\d+ (pages|page)\s*',  # np. "7 pages", "113 pages"
            r'\d+ (strona|strony)\s*',  # np. "1 strona", "2 strony"
            r'\d+ days ago —\s*',  # np. "4 days ago —"
            r'\d+ dni temu —\s*',  # np. "4 days ago —"
            r'cited by \d+ —\s*',  # np. "cited by 12 — "
            r'(?:by\s*)?[\w\s]+ \d{4} cited by \d+\s*', # np. "by John Doe 2024 cited by 10"
            r'by [A-Z][A-Za-z]+ [A-Z][A-Za-z]+ cited by \d+ years? ago'

        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text)

        text = text.translate(str.maketrans('', '', string.punctuation + "–_—·•"))
        text = re.sub(r'\u200b', '', text)
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


    def checkIfSnippetHasTestFormat(self, webGrams):
        ab = "ab"
        bc = "bc"
        cd = "cd"

        id_ab = 0
        id_bc = 0
        id_cd = 0
        
        for onegram in webGrams:
            if onegram == ab[id_ab]:
                id_ab += 1
                if id_ab == 2:
                    return True
                
            elif onegram == bc[id_bc]:
                id_bc += 1
                if id_bc == 2:
                    return True
                
            elif onegram == cd[id_cd]:    
                id_cd += 1                   
                if id_cd == 2:
                    return True
                
        return False


    def isNotContaminated(self, question, webContext):
        
        question = self.clearText(question)
        webContext = self.clearText(webContext)

        web_ngrams = self.getNgrams(webContext)

        if self.checkIfSnippetHasTestFormat(web_ngrams):
            return False, question, webContext

        q_ngrams= self.getNgrams(question)

        if not q_ngrams or not web_ngrams:
            return True, question, webContext

        similar_ngrams = self.getSimilarNgramsNum(q_ngrams, web_ngrams)

        if len(q_ngrams) > len(web_ngrams):
            if webContext in question:
                return False, question, webContext
            
            if similar_ngrams < math.ceil(len(web_ngrams) / 2):
                return True, question, webContext
            
        elif len(q_ngrams) < 5:
            if similar_ngrams <= len(q_ngrams) + 1:
                return True, question, webContext

        elif similar_ngrams < math.ceil(len(q_ngrams) / 2): 
                return True, question, webContext
         
        return False, question, webContext



    async def fetch(self, session, query, engine):
        try:
            async with self.semaphore: 
                async with session.get(f"http://localhost:8080/search?q={query}&engines={engine}&format=json") as response:
                    return await response.json()
        except Exception as e:
            print(f"\nQ: {query} Err: {str(e)}")
            return None
        

    async def fetchBraveAPI(self, session, query):
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            params = {
                "q": query,
                "count": 20,
                "text_decorations": "false",
                "result_filter": "web",
                "offset	": 0,
                "country": "pl"
            }
            async with self.semaphore:
                async with session.get(url, headers=headers, params=params) as response:
                    return await response.json()
        except Exception as e:
            print(f"\nQ: {query} Err: {str(e)}")
            return None



    async def get_web_context_async(self, doc, task):
        
        if self.key == "":
            self.GetMatchingQuestionKey(doc, task)

        if self.key is None:
            doc['WebContext'] = "None"
            self.questionWithoutContext.append("error: unknown key")
            return doc
        else: 
            query = doc[self.key]
        
        async with aiohttp.ClientSession() as session:
            try:
                
                firstIteration = True
                processedSnippets = 0
                for engine in ["google", "brave", "ddg", "braveAPI", None]:
                    if engine is None:
                        self.noContext += 1
                        self.contaminatedWebContext -= processedSnippets
                        doc['WebContext'] = "None"
                        self.questionWithoutContext.append(query)
                        return doc
                    else:

                        if engine == "braveAPI":
                            print("\n--=# BRAVE-API #=--\n")
                            async with aiohttp.ClientSession() as session:
                                results = await self.fetchBraveAPI(session, query)

                            if not results or results is None or "web" not in results:
                                continue

                            results = results["web"]["results"]
                        else:
                            results = await self.fetch(session, query, engine)

                            if not results or results is None or "results" not in results:
                                continue

                            results = results["results"]

                        for result in results:

                            if engine == "braveAPI":
                                domain = result["profile"]["long_name"]
                                content = result["description"]
                                url = result["profile"]["url"]
                            else:
                                domain = result["parsed_url"][1]
                                content = result["content"]
                                url = result["url"]

                            processedSnippets += 1

                            if domain in excludedDomains or domain in self.contaminatedDomains:
                                self._handle_excluded_domain(domain)
                                firstIteration = self._handle_contaminated_WebContext(firstIteration)
                            else:

                                notconaminated, question, webContext = self.isNotContaminated(query, content)
                                if domain.endswith("wikipedia.org") or notconaminated:
                                    doc['WebContext'] = webContext
                                    self.GoodUrls.append({"snippetIndex": processedSnippets, "query": question, "content": webContext, "url": url, "engine": engine})
                                    self.validSnippetIndexSum += processedSnippets
                                    return doc
                                else:
                                    self.contaminatedUrls.append({"snippetIndex": processedSnippets, "query": question, "content": webContext, "url": url, "engine": engine})
                                    firstIteration = self._handle_contaminated_WebContext(firstIteration)
                                

            except Exception as e:
                print(f"\nQ: {query} get_web_context_async Err: {str(e)}")
                doc['WebContext'] = "None"
                self.questionWithoutContext.append(query)
                return doc

    def _handle_contaminated_WebContext(self,firstIteration):
        self.contaminatedWebContext += 1
        if firstIteration:
            self.contaminatedQueries += 1
            return False

    def _handle_excluded_domain(self, domain):
        if domain in self.suspectedDomains:
            self.suspectedDomains[domain] += 1
            if self.suspectedDomains[domain] >= 10:
                self.contaminatedDomains.append(domain)
        else:
            self.suspectedDomains[domain] = 1
    


    async def process_all(self,task,testType):
        tasks = [self.get_web_context_async(doc, task) for doc in task.dataset[testType]]
        
        results = []
        for t in tqdm(asyncio.as_completed(tasks), total=len(task.dataset[testType]), desc="Questions", unit="Q"): # gruncocoa sum(1 for _ in task.dataset[testType])
            results.append(await t)

        tasks = None
        return datasets.Dataset.from_dict({key: [d[key] for d in results] for key in results[0]})
    



    def GetMatchingQuestionKey(self,doc,task):
        try:
            keys_to_check = [
                'question',
                "premise",
                'hypothesis',
                "sentence1",
                "sentence",
                "question",
                "question1",
                "criteria",
                "context",
                "text",
                "query",
                "input",
                "qtext",
                None
            ]

            if task.question_key is not None:
                keys_to_check.insert(0,task.question_key)
            
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