### Command:

### 1. Najpierw należy uruchomić wyszukirawkę SearXNG

### 2. Następnie należy uruchomić lm_evaluation_harness

``` bash
--web_access (-web) 			|: powoduje, że do każdego pytania z testowej części korpusu zostanie doklejony snippet z wyszukiwarki internetoej (użycie --web_acess bez użcia -wda niezalecane)
--web_data_action (-wda) <load/save>	|: wymagane użycie również -web: wczytuje istniejący zmodyfikowany korpus (load) lub do tworzy nowy korpus z kontekstem z internetu (save). Uwaga standardowo szuka/tworzy korspus z sufixem "eval"
--file_sufix (-fs) <string>		|: wymagane użycie równieś -fs :pwoduje że będze wczytywany/zapisywany korpus o niesatdardowym sufixie
--question_key (-qk) <string>		|: wyznacza klucz po którym będzie szukana treść dokumentu, która zostanie przekazana do przeglądarki jako pytanie


lm_eval --model hf --model_args pretrained=openai-community/openai-gpt --tasks arc_easy --device cuda:0 --batch_size auto --web_access --web_data_action save --file_sufix TEST_1
```
### Dodatkowe informacje:
- Dane zapisywane są w: **./cache/huggingface/datasets/<nazwa_dataset>/web_access_nazwaKorpusu_sufix**
- Korspus z dostepem do internetu o nazwie web_access_nazwaKorpusu_sufix
- Dodatkowy plik NazwaKorpusu_web_sufix.json zawierający ciekawe dane, takie jak:

``` python
 data_to_save = {
            "dataset_name": f"web_access_{self.DATASET_NAME}_{self.file_sufix}",
            "question_count_in_dataset": int,
            "queries_without_web_context_count": list,
            "contaminated_queries_count": int,
            "processed_contaminated_urls_count": int,
            "valid_urls_count": int,
            "most_contaminated_domains": list,
            "questions_without_webContext": list,
            "contaminated_urls": list,
            "valid_urls": list
        }     
```


### Models:
* openai-community/openai-gpt
* openai-community/gpt2
* openai-community/gpt2-large
* microsoft/Phi-3.5-mini-instruct
* meta-llama/Llama-3.2-1B
* meta-llama/Llama-3.2-1B-Instruct
* meta-llama/Meta-Llama-3.1-8B
* google/gemma-2-2b
* Qwen/Qwen2.5-1.5B-Instruct

### Logs:
``` python
eval_logger.info(f"")
```
