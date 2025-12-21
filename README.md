# Konteneryzacja rozwiązania ML i jego testy wydajności (np. docker)

## Autorzy
- Aleksander Karpiuk
- Szymon Stachura

## Opis projektu 
Celem projektu jest porównanie dwóch podejść do serwowania modeli uczenia maszynowego:
- FastAPI jako lekka i szybka opcja do tworzenia API dla modeli ML
- Ray Serve jako bardziej zaawansowane narzędzie do skalowalnego serwowania modeli ML
- Testy wydajnościowe obu podejść przy użyciu różnych modeli ML (MultinomialNB oraz SVC) oraz narzędzia Locust do symulacji obciążenia.
- Konteneryzacja obu rozwiązań przy użyciu Dockera w celu zapewnienia spójnego środowiska uruchomieniowego.
- Analiza wyników testów wydajnościowych w kontekście liczby obsłużonych zapytań, czasu odpowiedzi oraz stabilności serwerów.

## Wymagania wstępne
- Python 3.12
- Docker

oraz biblioteki Python zawarte w pliku `requirements.txt`.

## Pliki aplikacji

### Konfiguracja

Plik zawiera funkcje do ładowania modeli ML oraz przewidywania na podstawie danych wejściowych. Ponadto konfigurację loggera dla serwera FastAPI, który obsługuje również zapis logów do plików potrzebnych do analizy wydajności.

### Server FastAPI

Zaimplementowano model na podstawie `BaseModel` z biblioteki Pydantic, który definiuje strukturę danych wejściowych dla endpointu predykcji (tekst do zaklasyfikowania, typ modelu (`SVC` lub `MultinomialNB`)).

Endpoint `/predict` obsługuje żądania POST, przyjmując dane wejściowe w formacie JSON, wykonuje predykcję za pomocą wybranego modelu ML i zwraca wynik w formacie JSON. Dodatkowo loguje czas przetwarzania każdego zapytania.

Oprócz tego endpoity takie jak status serwera oraz domyslny root endpoint z informacją o serwerze.

### Server Ray Serve

Podobnie jak w przypadku FastAPI, zdefiniowano model danych wejściowych oraz endpoint `/predict`, który obsługuje żądania POST. Wykorzystano Ray Serve do zarządzania serwerem i skalowalnością. Logowanie czasu przetwarzania zapytań jest również zaimplementowane.

Oprócz tego endpoity takie jak status serwera oraz domyslny root endpoint z informacją o serwerze.

## Testy wydajnościowe

### Skrypt `test_scripts/run_performance_test.py`

Na początku pliku można zadeklarować, dla jakich parametrów ma wykonać się test:
- docker/local - czy testy mają być wykonywane na serwerach uruchomionych lokalnie czy w kontenerach Docker
- liczba zapytań do wysłania (200 lub 3000)
- typ serwera - fastapi/ray
- typ modelu - svc/nb
Asynchroniczny skrypt generuje zapytania, które następnie wysyła do odpowiedniego serwera i mierzy czas odpowiedzi oraz liczbę poprawnie przetworzonych zapytań. Wyniki są zapisywane do pliku .csv.

### Skrypt `test_scripts/run_locust_test.py`

Plik konfiguracyjny dla narzędzia Locust, które symuluje obciążenie serwera poprzez generowanie wielu równoczesnych użytkowników wysyłających zapytania do endpointu predykcji. Zadanie ma symulować normalny ruch użytkowników na serwerze. Wybrano parametry oczekiwania pomiędzy wysyłaniem następnych requestów pomiędzy 0.5 sekundy a 2 sekundy. Zdefiniowano jak wyglądać ma zapytanie dla serwera Rat.

## Wyniki 

### MultinomialNB
Wyniki uzyskane przy wywołaniu skryptu `test_scripts/run_performance_test.py`. 
Widzimy, że Ray Serve radzi sobie lepiej z obsługą większej liczby zapytań na sekundę. 
W przypadku MultinomialNB różnica jest mniej więcej pięciokrotna przy 3000 zapytań, 
gdy mówimy o przetwarzaniu przez sam serwer.
Ray serve ma również większą ilość poprawnie przetworzonych zapytań. Niemniej kolumna `avg_duration_seconds`
wskazuje, że czas odpowiedzi jest dłuższy niż w przypadku FastAPI. Może to wynikać z faktu, że Ray Serve
używa dodatkowych mechanizmów do zarządzania ruchem i skalowalnością, co może wprowadzać pewne opóźnienia.

| server_type | env_type | n_requests | n_success | avg_dur_sec | avg_log_czas_ms |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **fastapi** | docker | 200 | 200 | 0.23 | 59.47 |
| **ray** | docker | 200 | 200 | 0.98 | 16.28 |
| **fastapi** | local | 200 | 200 | 0.19 | 32.00 |
| **ray** | local | 200 | 200 | 0.70 | 12.08 |
| **fastapi** | docker | 3000 | 2957 | 1.77 | 72.56 |
| **ray** | docker | 3000 | 2978 | 11.39 | 15.23 |
| **fastapi** | local | 3000 | 2957 | 1.60 | 58.35 |
| **ray** | local | 3000 | 2978 | 8.30 | 10.56 |

### SVC
Wyniki uzyskane przy wywołaniu skryptu `test_scripts/run_performance_test.py`. 
Widzimy, że Ray Serve radzi sobie lepiej z obsługą większej liczby zapytań na sekundę. 
W przypadku SVC różnica jest jeszcze bardziej widoczna przy 3000 zapytań. Tutaj różnica jest 
ponad dziesięciokrotna. Ray serve ma również większą ilość poprawnie przetworzonych zapytań. 
Także kolumna `avg_duration_seconds` ma mniejszą różnicę przy powrocie zapytań do klienta. 
Model SVC z natury jest bardziej złożony obliczeniowo niż MultinomialNB. Pokazuje to, że 
Ray idealnie radzi sobie z obsługą bardziej złożonych modeli pod kątem czasu przetwarzania serwera.

| server_type | env_type | n_requests  | n_success | avg_dur_sec | avg_log_czas_ms |
| :--- | :--- |:-----------:|:---------:| :---: | :---: |
| **fastapi** | docker |     200     |    200    | 2.09 | 1053.30 |
| **ray** | docker |     200     |    200    | 2.13 | 53.48 |
| **fastapi** | local |     200     |    200    | 2.62 | 831.90 |
| **ray** | local |     200     |    200    | 2.77 | 69.58 |
| **fastapi** | docker |    3000     |   2957    | 20.54 | 1036.45 |
| **ray** | docker |    3000     |   2978    | 28.92 | 50.19 |
| **fastapi** | local |    3000     |   2957    | 24.42 | 975.21 |
| **ray** | local |    3000     |   2978    | 32.99 | 60.22 |


### SVC w teście z Locust (wyłącznie Ray Serve)
- Przypadek 100 użytkowników dodawanych 10 na sekundę

Wyniki na serwerze Ray uruchominym na lokalnej maszynie wykazały dobrą wydajność i stabilność serwera. Odpowiedzi poprawne były udzielane z częstotliwością około 70 RPS.

Wyniki na dockerowym serwerze Ray wykazały równie dobrą wydajność i stabilność serwera. Odpowiedzi poprawne były udzielane z częstotliwością około 80 RPS, lecz czas oczekiwania na odpowiedź był lekko wyższy niż w przypadku lokalnego serwera.

- Przypadek 1000 użytkowników dodawanych 20 na sekundę

Wyniki na serwerze Ray uruchominym na lokalnej maszynie wykazały niższą wydajność w porównaniu do poprzedniego testu, ale serwer nadal radził sobie dobrze z obsługą zapytań. Odpowiedzi poprawne były udzielane z częstotliwością około 60 RPS. Widać, że mogło być kilka przypadków braku odpowiedzi, gdyż 95 percentyl pokazuje wydłużony czas oczekiwania na odpowiedź. 

Wyniki na dockerowym serwerze Ray wykazały podobne wyniki zarówno pod kątem RPS, jak i czasów odpowiedzi dla 95 percentyla. Niemniej średnia odpowiedź była mniej więcej dwa razy dłuższa w porównaniu z lokalną implementacją. 

- Przypadek 2500 użytkowników dodawanych 100 na sekundę 

Wyniki na serwerze Ray uruchominym na lokalnej maszynie wykazały, że przy takim obciążeniu i przedstawionej konfiguracji, nie radzi sobie zbyt dobrze z obsługą zapytań - część z nich była zamykana z powodu przekroczenia limitu czasu, lub odłączenia użytkownika. 

Wyniki na dockerowym serwerze Ray wykazały znaczną niewydolność serwera i przerwanie jego działania w momencie dojścia do 2500 użytkowników. Serwer przesyłał wyłącznie błędy związane z errorami, przy czym nie było żadnej pozytywnie zakończonej odpowiedzi od serwera. 

## Źródła
- Zastosowanie kolejki zapytań API - [[Link]](https://medium.com/modern-nlp/101-for-serving-ml-models-10217c9f0764) 
- Przegląd opcji serwowania modeli ML - [[Link]](https://github.com/awesome-mlops/awesome-ml-serving)
- Ray Serve docks - [[Link]](https://docs.ray.io/en/latest/serve/tutorials/serve-ml-models.html)
- Ray Serve medium przykład - [[Link]](https://medium.com/@gouravkumargupta10/guide-to-model-serving-using-ray-800e41ded422)
- Locust docs - [[Link]](https://docs.locust.io/en/stable/)