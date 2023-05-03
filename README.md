# NADA Soda
Repo for generelt dockerimage brukt av soda-jobber som kjører i teamnamespaces. Se eksempel for naisjobb [her](https://github.com/navikt/dp-nada-soda). Se skisse av hvordan tester kjøres og sentralisert samling av resultater samt varsling av avvik til slack [her](https://github.com/navikt/nada-soda-service#skisse).

## Build and push image
````bash
docker build -t ghcr.io/navikt/nada-soda:<tag> .
docker push ghcr.io/navikt/nada-soda:<tag>
````
