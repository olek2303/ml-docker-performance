# Uruchamianie obrazów
Będąc w głównym katalogu projektu możemy wykonać polecenia:

- Plik Dockerfile-server:
```bash
docker build -t ml-server -f docker/Dockerfile-server . 
docker run -p 8000:8000 --name ml-server ml-server 
```

- Plik Dockerfile-ray:
```bash
docker build -t ml-ray -f docker/Dockerfile-ray .
docker run -p 8000:8000 --name ml-ray ml-ray 
```
