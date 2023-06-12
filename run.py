import os
import yaml
import logging
import requests
from datetime import datetime
from soda.scan import Scan

class NadaSoda:
    def __init__(
        self,
        soda_config: str, 
        soda_checks_folder: str,
        slack_channel : str
    ) -> None:
        self._soda_config = soda_config
        self._soda_checks_folder = soda_checks_folder
        self._slack_channel = slack_channel if slack_channel.startswith("#") else "#"+slack_channel
        self._soda_api = os.getenv("SODA_API")

    def run(self) -> None:
        for f in os.listdir(self._soda_checks_folder):
            if f.endswith(".yaml"):
                gcp_project, dataset, scan = self._run_scan(f)
                self._publish_results(gcp_project, dataset, scan)

    def _run_scan(self, f: str) -> tuple[str, str, Scan]:
        s = Scan()
        self._add_configuration_yaml(s, f)
        dataset = f.split(".")[0]
        s.set_data_source_name(dataset)
        s.add_sodacl_yaml_file(f"{self._soda_checks_folder}/{f}")
        s.execute()
        return self._get_gcp_project(dataset), dataset, s

    def _add_configuration_yaml(self, s: Scan, config_file: str) -> None:
        with open(config_file, "r") as f:
            cfg = yaml.safe_load(f.read())
        cfg["send_anonymous_usage_stats"] = False
        s.add_configuration_yaml_str(yaml.dump(cfg))

    def _get_gcp_project(self, dataset: str) -> str:
        with open(self._soda_config, "r") as f:
            cfg = yaml.safe_load(f)
        for k in cfg.keys():
            if cfg[k]["connection"]["dataset"] == dataset:
                return cfg[k]["connection"]["project_id"]

        raise KeyError(f"dataset {dataset} not found in config")

    def _publish_results(self, gcp_project: str, dataset: str, scan: Scan):
        results = [self._create_soda_result(r) for r in scan.get_scan_results().get("checks")]
        res = requests.post(f"{self._soda_api}/soda/new", json={
            "gcpProject": gcp_project,
            "dataset": dataset,
            "slackChannel": self._slack_channel,
            "testResults": results
        })
        res.raise_for_status()

    def _create_soda_result(self, res: dict) -> dict:
        return {
            "id": res["identity"],
            "table": res["table"],
            "test": res["name"],
            "definition": res["definition"],
            "metrics": res["metrics"],
            "outcome": res["outcome"],
            "time": datetime.now().isoformat(),
            "resourceAttributes": res.get("resourceAttributes"),
            "column": res.get("column"),
            "type": res.get("type"),
            "filter": res.get("filter"),
            "slack": self._slack_channel
        }

if __name__ == "__main__":
    try:
        config_path = os.environ["SODA_CONFIG"]
        checks_path = os.environ["SODA_CHECKS_FOLDER"]
        slack_channel = os.environ["SLACK_CHANNEL"]
    except KeyError:
        logging.error("Environment variables SODA_CONFIG, SODA_CHECKS_FOLDER and SLACK_CHANNEL are all required to run this script")
        exit(1)
    
    soda_checks = NadaSoda(config_path, checks_path, slack_channel)
    try:
        soda_checks.run()
    except:
        logging.error("Running SODA checks failed")
        raise
