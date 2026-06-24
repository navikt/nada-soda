import logging
import os
from datetime import datetime

import requests
from soda_core.contracts import verify_contract_locally
from soda_core.contracts.contract_verification import CheckOutcome

logging.basicConfig(level=logging.INFO)


class NadaSoda:
    def __init__(
        self,
        soda_config: str,
        soda_checks_folder: str,
        slack_channel: str,
    ) -> None:
        self._soda_config = soda_config
        self._soda_checks_folder = soda_checks_folder
        self._slack_channel = slack_channel if slack_channel.startswith("#") else "#" + slack_channel
        self._soda_api = os.getenv("SODA_API")
        self._docker_image = os.getenv("NAIS_APP_IMAGE")

    def run(self) -> None:
        for f in os.listdir(self._soda_checks_folder):
            if not f.endswith(".yaml") and not f.endswith(".yml"):
                continue
            contract_path = os.path.join(self._soda_checks_folder, f)
            logging.info(f"Running contract {f}")
            self._run_and_publish(contract_path)
            logging.info(f"Successfully published results from contract {f}")

    def _run_and_publish(self, contract_path: str) -> None:
        result = verify_contract_locally(
            contract_file_path=contract_path,
            data_source_file_path=self._soda_config,
        )
        for cvr in result.contract_verification_results:
            prefixes = cvr.contract.dataset_prefix or []
            gcp_project = prefixes[0] if len(prefixes) > 0 else ""
            bq_dataset = prefixes[1] if len(prefixes) > 1 else ""
            table = cvr.contract.dataset_name or ""

            test_results = [self._create_test_result(cr, table) for cr in cvr.check_results]
            error_str = cvr.get_errors_str() if cvr.has_errors else None

            res = requests.post(f"{self._soda_api}/soda/new", json={
                "gcpProject": gcp_project,
                "dataset": bq_dataset,
                "slackChannel": self._slack_channel,
                "slackNotifyOnScanPassed": os.getenv("NOTIFY_OK_SCAN_STATUS"),
                "dockerImage": self._docker_image,
                "testResults": test_results,
                "configError": error_str,
            })
            res.raise_for_status()

    def _create_test_result(self, check_result, table: str) -> dict:
        metric_values = None
        if check_result.diagnostic_metric_values:
            metric_values = {
                k: v for k, v in check_result.diagnostic_metric_values.items()
                if isinstance(v, (int, float, str, bool))
            }

        return {
            "id": check_result.check.identity,
            "table": table,
            "test": check_result.check.name or check_result.check.definition,
            "definition": check_result.check.definition,
            "metrics": metric_values,
            "outcome": check_result.outcome.name,
            "time": datetime.now().isoformat(),
            "column": check_result.check.column_name or "",
            "type": check_result.check.type or "",
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
    except Exception:
        logging.error("Running SODA checks failed")
        raise
