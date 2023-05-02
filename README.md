# NADA Soda
Naisjob example for periodically running [soda](https://github.com/sodadata/soda-core) checks against BigQuery tables and posting data quality errors to slack.

## Prerequisites
The python script requires

- A [soda config](https://docs.soda.io/soda/connect-bigquery.html#connection-configuration) for connecting to one or several BigQuery datasource(s). See [config example](https://github.com/navikt/nada-soda/blob/main/.local/soda-config/config.yaml) for configuring this for nais.
- One or several [soda check config(s)](https://docs.soda.io/soda-cl/soda-cl-overview.html) describing the checks you want to perform on the BigQuery tables. See [config folder](https://github.com/navikt/nada-soda/tree/main/.local/soda-checks) for examples.
- The slack channel where you want to post data quality errors
- A slack token for a slack app allowed to post to channels in the NAV IT workspace on slack

All of the above requirements must be configured with environment variables as described in [Required environment variables](#required-environment-variables) below.

The soda config and the soda check files needs to be mounted into the container environment on nais. In this example these configurations files are mounted from configmaps deployed together with the naisjob to the cluster. See [.nais folder](https://github.com/navikt/nada-soda/tree/main/.nais) for example on how to do this.

You will also need additional [project level iam roles](https://github.com/navikt/nada-soda/blob/main/.nais/naisjob.yaml#L32-L47) for the naisjob service account in order to be allowed to perform the soda checks.

Note: The script requires that a datasource name matches the file name for the corresponding data quality tests, e.g. [./local/soda-checks/doc_demo.yaml](https://github.com/navikt/nada-soda/tree/main/.local/soda-checks) without file extension must match the datasource name `doc_demo` in the [connection config](https://github.com/navikt/nada-soda/blob/main/.local/soda-config/config.yaml#L1).

### Required environment variables
- `SODA_CONFIG`: Path to soda config file
- `SODA_CHECKS_FOLDER`: Path to folder containing soda check files for BigQuery datasets
- `SLACK_CHANNEL`: Desired slack channel for posting data quality errors

## Build and push image
````bash
docker build -t ghcr.io/navikt/<image> .
docker push ghcr.io/navikt/<image>
````
Replace `<image>` above.