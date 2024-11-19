# AMU-Master-Thesis

## Projekt badawczo-rozwojowy oraz praca magisterska

### Tytuł: "Ewaluacja dużych modeli językowych zintegrowanych z wiedzą zewnętrzną."

#### Zamysł i plan działania:
    A. Badamy klasyczną odpowiedź modelu na dane pytanie testowe.
    B. Badamy odpowiedź modelu na dane pytanie testowe z dodatkowym kontekstem (wiedzą z internetu):
        1. Czytamy zadane pytanie (możemy użyć modelu aby on odpowiedział o co warto zapytać w wyszukiwarce)
        2. Uruchamiamy wyszukiwarkę i pozyskujemy potrzebną wiedzę
        3. Wstępne obrobienie zdobytych danych (preprocessing)
        4. Uruchomienie modelu językowego - dołączenie pozyskanych informacji jako kontekst + pytanie
    C. Porównujemy wyniki.


#### Będę korzystać z:
1. LM-evaluation-harness [narzędzie open-source]
2. Search Engine API np.: od Bing/Google/Brave/SearXNG
3. Python / Pythorch
4. Benchmark dla LMM -> np.: MMLU (Massive Mulitask language understanding) / ARC - (AI Reasoning chalange) / DYK (Did you know? Polski)
5. Jakiś model językowy:  
    a. API -> płatne - np.: GPT3.5-turbo / GPT-4.0
    b. odpadalany lokalnie mniejszy model LLM (open-source) np.: GPT-2  / tinyllama (WAŻNA JEST WIELKOŚĆ OKNA KONTEKSTOWEGO!)
