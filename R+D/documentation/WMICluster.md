# Przydatne informacje przy korzystaniu z klastra obliczeniowego UAM

Dokumnetacja klastra obliczeniowego: https://cluster.wmi.amu.edu.pl/

Dane dostępowe:
- Login: ***s444820***
- Konto ważne do: ***2025-09-01***
- quota -> polecenia aktualnego użycia

<br>

### UWAGA 
**Po zakończeniu pracy należy przerwać maksymalną rezerwacje!**

``` bash
scancel <id>
```

<br>

## Uruchamianie conda

``` bash
module load anaconda
-- jeśli nie istnieje -> conda create --name <nazwa> python=3.12
conda activate <nazwa> 

```

## Podłączenie się do Klastra Obliczeniowego:

### kroki:
1. Podłącz się przez ssh do maszyny dostępowej: 
   
   ``` bash 
   ssh s444820@access.cluster.wmi.amu.edu.pl
   ```

2. Zarządaj maksymalnej rezerwacji GPU

    ``` bash
    salloc --no-shell --partition=gpu --exclusive --gres=gpu:1 --time=12:00:0
    ```
    Otrzymasz ID sesji oraz nazwę server np.: g1n1 (**zapisz je sobie!**)

3. Podłącz się przez ssh do klastra obliczeniowego:
   
   ``` bash
    ssh g1n1
   ```

4. Stwórz osobny katalog na projekt lub podłacz się do już istniejącego:

    A. Przejście do instiejącego

    ``` bash
    cd /work/s444820
    cd llm-workshop
    ```

    
    B. Tworzenie nowego
    ``` bash
    cd /work/s444820
    mkdir llm-workshop
    cd llm-workshop
    ```

5. Warto używaz **tmux** lub **screen** aby pracować na kilku powłokach w jendej konsoli:

    jak używać *screen*: https://www.linux.pl/2021/02/15/wirtualne-konsole-w-systemie-linux-screen/


<br>
<br>

## Praca z model językowym LLaMa3:8b

1. Pobranie obrazu Docker i konwersja do formatu Singularity/Apptainer:

    ``` bash
    apptainer build ollama.sif docker://ollama/ollama:0.1.37
    ```

2. Należy utworzyć katalog na dane, który będzie zamontowany do uruchomionego kontenera:

    ``` bash
    mkdir ollama_data
    ```

3.  W osobnej powłoce można odpalić nvtop i obserwować GPU. (**opcjonalne**)

    ``` bash
    nvtop
    ```

4. Uruchomienie ollama z parametrami:

   1. --containall - nie montuje automatycznie zasobów do kontenera (omijamy w celach bezpieczeństwa, bo to będzie usługa używana przez innych)
   2. --bind /tmp:/tmp - montujemy lokalny 50GB katalog /tmp
   3. --bind ./ollama_data:/home/s444820/ - montujemy katalog na dane
   4. --nv - włączamy przekazanie GPU do kontenera
   
    ``` bash
    apptainer run --containall --bind /tmp:/tmp --bind ./ollama_data:/home/s444820/ --nv ollama.sif
    ```

<br>
<br>

## Open WebUI

1. Podobnie jak wyżej, budujemy, tworzymy zasoby i uruchamiamy:

    ``` bash
    apptainer build openwebui.sif docker://ghcr.io/open-webui/open-webui:v0.1.124

    mkdir webui_data
    ```

2. Poza katalogiem na dane kontener wymaga utworzenia warstwy pozwalającej na zapis - domyślnie wszystkie kontenery Singularity/Apptainer są tylko-do-odczytu aby umożliwić ich współbieżne uruchamianie.

    ``` bash
    apptainer overlay create --size 1024 ./webui_overlay.img
    ```

3. Kontener ma też niestandardową strukturę i wymaga ręcznego wywołania skryptu startowego:

    ``` bash
    apptainer exec --overlay ./webui_overlay.img --containall --bind ./webui_data:/app/backend/data openwebui.sif /app/backend/start.sh
    ```

    Uruchamianie aplikacji trwa chwilę, należy poczekać na komunikaty:

    *INFO:apps.litellm.main:Subprocess started successfully*.

4. Aplikacja dostępna jest pod adresem zależnym od aktualnego węzła, na przykład http://g1n1.cluster.wmi.amu.edu.pl:8080/

    Należy jak najszybciej przejść pod ten adres i utworzyć konto - będzie ono kontem administracyjnym więc powinno mieć mocne hasło. E-mail nie ma znaczenia, jest tylko loginem.

    Po zalogowaniu należy przejść do ustawień:
    1. nazwa użytkownika w lewym dolnym rogu -> Settings
    2. Connections -> Ollama Base URL: http://127.0.0.1:11434 -> kliknąć w ikonę odświeżenia, powinien pojawić się komunikat
    3. Models -> Pull a model from Ollama.com: llama3:8b -> kliknąć w ikonę pobierania

5. Aby umożliwić uczestnikom kursu rejestrację i logowanie bez potrzeby akceptacji przez administratora należy przejść do ustawień administracyjnych:

   1. nazwa użytkownika w lewym dolnym rogu -> Admin Panel -> Admin Settings w prawym górnym rogu
   2. General -> Default User Role: User
   3. Save
   W sekcji Users można także wybrać modele udostępnione użytkownikom, gdyby była potrzeba ich ograniczenia do danego kursu.


## Miejsce przechowywania zapisanych modeli, ścniągniętych z HuggingFace:

``` bash
cd ~/.cache/huggingface/hub ```
rm -rf <nazwa_modelu>
```

## Praca z kontenerami:

W klastrze obliczeniowym UAM jest znaczące ograniczenie korzystania z kontenerów dlatego trzeba korzystać z apptainer

``` bash
apptainer build --sandbox my_sandbox_dir sxng.sif
cd my_sandbox_dir/etc/
mkdir searxng
cd searchxng/
vim settings.yml
vim uwsgi.ini
apptainer build new_good.sif my_sandbox_dir
apptainer run new_good.sif
```


## Ważne informacje od administartora:
1. Brak ryzyka, że dostep zostanie odcięty bez wcześniejszego powiadomienia. 

2. Dane nie będą usuwane bez bez odpowiedniej infnormacji.

3. Nie będzie problemu z przedłużeniem ważności

4. Można instalować oprogramowanie i pobierać nowe dane/modele/zasoby (Bierze się za to odpowiedzialność)

5. Uwaga na ilość zajęte miejsca i zwalniać je na bieżąco, jeśli dany zasób nie będzie już dostępny.