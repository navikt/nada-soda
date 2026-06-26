# NADA Soda
 
 Felles Docker-images for Soda-jobber som kjører datakvalitetstester mot BigQuery i Nais.
 
 Se skisse av hvordan tester kjøres, sentralisert samling av resultater, og varsling av avvik til Slack i 
[navikt/nada-soda-service](https://github.com/navikt/nada-soda-service#skisse).  
 Se eksempel på oppsett av en Naisjobb i [navikt/dp-nada-soda](https://github.com/navikt/dp-nada-soda).
 
 ## Images
 
 Det finnes to images — velg basert på hvilken versjon av Soda du bruker:

 | GAR-image (bruk i naisjob) | GHCR-image (Dependabot-tracking) | Soda-versjon | Format |
 |----------------------------|----------------------------------|-------------|--------|
 | `europe-north1-docker.pkg.dev/nais-management-233d/nada/nada-soda:<tag>` | `ghcr.io/navikt/nada-soda/soda:<tag>` | v3 (SodaCL) | En sjekk-fil per BigQuery-datasett |
 | `europe-north1-docker.pkg.dev/nais-management-233d/nada/nada-soda-contracts:<tag>` | `ghcr.io/navikt/nada-soda/soda-contracts:<tag>` | v4 (Contracts) | En kontrakt-fil per tabell |

 Bruk GAR-imaget i Naisjob-spesifikasjonen. GHCR-imaget brukes av Dependabot i [navikt/dp-nada-soda](https://github.com/navikt/dp-nada-soda) for automatisk oppdatering av tags.

 Nye tags publiseres automatisk ved push til `main` (soda-contracts) og `v3`-branchen (soda).  
 Se [releases](https://github.com/navikt/nada-soda/releases) for tilgjengelige tags.
 
 ## Miljøvariabler
 
 | Variabel | Påkrevd | Beskrivelse |
 |----------|---------|-------------|
 | `SODA_CONFIG` | Ja | Sti til data source config-fil |
 | `SODA_CHECKS_FOLDER` | Ja | Sti til mappe med sjekk-filer / kontrakt-filer |
 | `SLACK_CHANNEL` | Ja | Slack-kanal for datakvalitetsvarsler |
 | `SODA_API` | Ja | URL til nada-soda-service |
 | `NOTIFY_OK_SCAN_STATUS` | Nei | Sett til `"true"` for Slack-varsling ved vellykkede kjøringer |
 
 ## Migrasjon fra v3 til v4
 
 v4 bruker et nytt format kalt [Data Contracts](https://docs.soda.io/reference/contract-language-reference). De viktigste endringene:
 
 - **Én fil per tabell** (v3 hadde én fil per BigQuery-datasett med flere tabeller)
 - **Nytt config-format** for data source
 - **Nytt image**: `soda-contracts` i stedet for `soda`
 
 Se [navikt/dp-nada-soda](https://github.com/navikt/dp-nada-soda) for konkrete før/etter-eksempler i `.nais/dev/soda/` (v3) og 
`.nais/dev/soda-contracts/` (v4).