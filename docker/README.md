# Uruchamianie obrazów
Będąc w głównym katalogu projektu możemy wykonać polecenia:

- Plik Dockerfile-server:
```bash
docker build -t ml-server -f docker/Dockerfile . 
docker run -p 8000:8000 ml-server
```

