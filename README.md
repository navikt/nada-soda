# NADA Soda
 
 Felles Docker-image med Soda v4 for datakvalitetstester mot BigQuery i Nais.
 
 Se skisse av hvordan tester kjøres, sentralisert samling av resultater, og varsling av avvik til Slack i 
[navikt/nada-soda-service](https://github.com/navikt/nada-soda-service#skisse).  
 Se eksempel på oppsett av en Naisjobb i [navikt/dp-nada-soda](https://github.com/navikt/dp-nada-soda).
 
 ## Image
 
 Imaget bruker Soda v4 med [Data Contracts](https://docs.soda.io/reference/contract-language-reference), med én kontraktfil per tabell.

 | GAR-image (bruk i Naisjobb) | GHCR-image (bruk med Dependabot) |
 |---------------------------|---------------------------------|
 | `europe-north1-docker.pkg.dev/nais-management-233d/nada/nada-soda-contracts:<tag>` | `ghcr.io/navikt/nada-soda/soda-contracts:<tag>` |

 Bruk GAR-imaget i Naisjobb-spesifikasjonen. GHCR-imaget brukes av Dependabot for automatisk oppdatering av tags.

 Nye tags publiseres automatisk ved push til `main`.  
 Se [releases](https://github.com/navikt/nada-soda/releases) for tilgjengelige tags.
 
 ## Miljøvariabler
 
 | Variabel | Påkrevd | Beskrivelse |
 |----------|---------|-------------|
 | `SODA_CONFIG` | Ja | Sti til data source config-fil |
 | `SODA_CHECKS_FOLDER` | Ja | Sti til mappe med kontraktfiler |
 | `SLACK_CHANNEL` | Ja | Slack-kanal for datakvalitetsvarsler |
 | `SODA_API` | Ja | URL til nada-soda-service |
 | `NOTIFY_OK_SCAN_STATUS` | Nei | Sett til `"true"` for Slack-varsling ved vellykkede kjøringer |
