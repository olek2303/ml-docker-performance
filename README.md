# Konteneryzacja rozwiązania ML i jego testy wydajności (np. docker)

## Autorzy
- Aleksander Karpiuk
- Szymon Stachura

## Wyniki 

### MultinomialNB
Widzimy, że Ray Serve radzi sobie lepiej z obsługą większej liczby zapytań na sekundę. 
W przypadku MultinomialNB różnica jest mniej więcej pięciokrotna przy 3000 zapytań, 
gdy mówimy o przetwarzaniu przez sam serwer.
Ray serve ma również większą ilość poprawnie przetworzonych zapytań. Niemniej kolumna `avg_duration_seconds`
wskazuje, że czas odpowiedzi jest dłuższy niż w przypadku FastAPI. Może to wynikać z faktu, że Ray Serve
używa dodatkowych mechanizmów do zarządzania ruchem i skalowalnością, co może wprowadzać pewne opóźnienia.
```
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|    | server_type   | env_type   |   num_requests |   num_success |   avg_duration_seconds |   avg_log_czas_ms |
+====+===============+============+================+===============+========================+===================+
|  0 | fastapi       | docker     |            200 |           200 |               0.228422 |           59.4654 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  1 | ray           | docker     |            200 |           200 |               0.977339 |           16.2774 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  4 | fastapi       | local      |            200 |           200 |               0.190382 |           32.0022 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  5 | ray           | local      |            200 |           200 |               0.701423 |           12.0785 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  8 | fastapi       | docker     |           3000 |          2957 |               1.77195  |           72.5565 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  9 | ray           | docker     |           3000 |          2978 |              11.3894   |           15.2283 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 12 | fastapi       | local      |           3000 |          2957 |               1.60412  |           58.3528 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 13 | ray           | local      |           3000 |          2978 |               8.29698  |           10.5589 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
```

### SVC
Widzimy, że Ray Serve radzi sobie lepiej z obsługą większej liczby zapytań na sekundę. 
W przypadku SVC różnica jest jeszcze bardziej widoczna przy 3000 zapytań. Tutaj różnica jest 
ponad dziesięciokrotna. Ray serve ma również większą ilość poprawnie przetworzonych zapytań. 
Także kolumna `avg_duration_seconds` ma mniejszą różnicę przy powrocie zapytań do klienta. 
Model SVC z natury jest bardziej złożony obliczeniowo niż MultinomialNB. Pokazuje to, że 
Ray idealnie radzi sobie z obsługą bardziej złożonych modeli pod kątem czasu przetwarzania serwera.
```
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|    | server_type   | env_type   |   num_requests |   num_success |   avg_duration_seconds |   avg_log_czas_ms |
+====+===============+============+================+===============+========================+===================+
|  2 | fastapi       | docker     |            200 |           200 |                2.09031 |         1053.3    |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  3 | ray           | docker     |            200 |           200 |                2.13235 |           53.4757 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  6 | fastapi       | local      |            200 |           200 |                2.61923 |          831.904  |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
|  7 | ray           | local      |            200 |           200 |                2.76588 |           69.5767 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 10 | fastapi       | docker     |           3000 |          2957 |               20.535   |         1036.45   |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 11 | ray           | docker     |           3000 |          2978 |               28.917   |           50.1939 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 14 | fastapi       | local      |           3000 |          2957 |               24.4234  |          975.209  |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
| 15 | ray           | local      |           3000 |          2978 |               32.9936  |           60.2185 |
+----+---------------+------------+----------------+---------------+------------------------+-------------------+
```


## Źródła
- Zastosowanie kolejki zapytań API - [[Link]](https://medium.com/modern-nlp/101-for-serving-ml-models-10217c9f0764) 
- Przegląd opcji serwowania modeli ML - [[Link]](https://github.com/awesome-mlops/awesome-ml-serving)
- JMeter - [[Link]](https://jmeter.apache.org/)
- Ray Serve docks - [[Link]](https://docs.ray.io/en/latest/serve/tutorials/serve-ml-models.html)
- Ray Serve medium przykład - [[Link]](https://medium.com/@gouravkumargupta10/guide-to-model-serving-using-ray-800e41ded422)