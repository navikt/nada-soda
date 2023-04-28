import os
import json
import yaml
import logging
import hashlib
from datetime import datetime
from soda.scan import Scan
from soda.execution.check.metric_check import MetricCheck
from slack_sdk import WebClient
from kafka import KafkaProducer

class NadaSoda:
    def __init__(
        self,
        soda_config: str, 
        soda_checks_folder: str, 
        slack_channel : str, 
        slack_token: str,
        kafka_topic: str
    ) -> None:
        self._soda_config = soda_config
        self._soda_checks_folder = soda_checks_folder
        self._slack_channel = slack_channel if slack_channel.startswith("#") else "#"+slack_channel
        self._slack_token = slack_token
        self._kafka_topic = kafka_topic

        self._kafka_producer = KafkaProducer(
            bootstrap_servers=os.environ["KAFKA_BROKERS"],
            security_protocol="SSL",
            ssl_cafile=os.environ["KAFKA_CA_PATH"],
            ssl_certfile=os.environ["KAFKA_CERTIFICATE_PATH"],
            ssl_keyfile=os.environ["KAFKA_PRIVATE_KEY_PATH"],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def run(self) -> None:
        for f in os.listdir(self._soda_checks_folder):
            gcp_project, dataset, scan = self._run_scan(f)
            if scan.has_check_warns_or_fails():
                self._post_slack(gcp_project, dataset, scan.get_checks_warn_or_fail())

            self._write_to_topic(gcp_project, dataset, scan)

    def _run_scan(self, f: str) -> tuple[str, str, Scan]:
        s = Scan()
        s.add_configuration_yaml_file(file_path=self._soda_config)
        dataset = f.split(".")[0]
        s.set_data_source_name(dataset)
        s.add_sodacl_yaml_file(f"{self._soda_checks_folder}/{f}")
        s.execute()
        return self._get_gcp_project(dataset), dataset, s

    def _get_gcp_project(self, dataset: str) -> str:
        with open(self._soda_config, "r") as f:
            cfg = yaml.safe_load(f)
        for k in cfg.keys():
            if cfg[k]["connection"]["dataset"] == dataset:
                return cfg[k]["connection"]["project_id"]

        raise KeyError(f"dataset {dataset} not found in config")

    def _post_slack(self, gcp_project: str, dataset: str, discrepancies: list[MetricCheck]) -> None:
        discrepancies_unpacked = self._unpack_and_remove_duplicates(discrepancies)
        errors, warnings = self._separate_errors_and_warnings(discrepancies_unpacked)

        top_block = self._create_slack_block()
        error_attachment = self._create_error_slack_attachment(gcp_project, dataset, errors) if len(errors) > 0 else None
        warning_attachment = self._create_warning_slack_attachment(gcp_project, dataset, errors) if len(warnings) > 0 else None
        self._post_slack_message([top_block], [error_attachment, warning_attachment])

    def _create_slack_block(self) -> dict:
        return {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Varsel om datakvalitetsavvik :gasp:"
            }
        }

    def _unpack_and_remove_duplicates(self, discrepancies: list[MetricCheck]) -> list[dict]:
        out = {}
        for e in discrepancies:
            err_dict = e.get_dict()
            if err_dict["identity"] not in out.keys():
                out[err_dict["identity"]] = err_dict
        return [out[key] for key in out.keys()]

    def _separate_errors_and_warnings(self, discrepancies: list[dict]) -> tuple[list[dict], list[dict]]:
        errors = []
        warnings = []
        for d in discrepancies:
            if d["outcome"] == "fail":
                errors.append(d)
            else:
                warnings.append(d)

        return errors, warnings

    def _create_error_slack_attachment(self, gcp_project: str, dataset: str, errors: list[dict]) -> dict:
        content = "\n".join([self._create_test_result(e) for e in errors])
        return {
            "fallback": "Tester med feil",
            "color": "#ff2d00",
            "author_name": f"{gcp_project}.{dataset}",
            "title": "Tester som feiler:",
            "text": content,
            "footer": "SODA Bot"
        }

    def _create_warning_slack_attachment(self, gcp_project: str, dataset: str, warnings: list[dict]) -> dict:
        content = "\n".join([self._create_test_result(e) for e in warnings])
        return {
            "fallback": "Tester med varslinger",
            "color": "#ffa500",
            "author_name": f"{gcp_project}.{dataset}",
            "title": "Tester med varslinger:",
            "text": content,
            "footer": "SODA Bot"
        }

    def _create_test_result(self, e: dict) -> str:
        return "\n".join([
            f"_*Tabell: {e['table']}*_" + (f" _*kolonne: {e.get('column')}*_" if e.get('column') else ""), 
            f"Test: {e['name']}"
        ])

    def _post_slack_message(self, blocks: list, attachments: list) -> None:
        client = WebClient(token=self._slack_token)
        client.chat_postMessage(channel=self._slack_channel,
                                text="Datakvalitetsavvik",
                                blocks=blocks,
                                attachments=attachments)

    def _write_to_topic(self, gcp_project: str, dataset: str, scan: Scan) -> None:
        for res in scan.get_scan_results()["checks"]:
            key, message = self._create_message(gcp_project, dataset, res)
            self._kafka_producer.send(self._kafka_topic, key=key.encode(), value=message)

    def _create_message(self, gcp_project: str, dataset: str, res: dict) -> tuple[str, dict]:
        message_key = self._create_message_key(gcp_project, dataset, res)
        test_ts = datetime.now().isoformat()
        return message_key, {
            "project": gcp_project,
            "dataset": dataset,
            "table": res["table"],
            "test": res["name"],
            "definition": res["definition"],
            "metrics": res["metrics"],
            "outcome": res["outcome"],
            "test_ts": test_ts,
            "resourceAttributes": res.get("resourceAttributes"),
            "column": res.get("column"),
            "type": res.get("type"),
            "filter": res.get("filter")
        }

    def _create_message_key(self, gcp_project: str, dataset: str, res: dict) -> str:
        return hashlib.md5(f"{gcp_project}.{dataset}.{res['table']}-{res['name']}".encode()).hexdigest()

if __name__ == "__main__":
    try:
        config_path = os.environ["SODA_CONFIG"]
        checks_path = os.environ["SODA_CHECKS_FOLDER"]
        slack_channel = os.environ["SLACK_CHANNEL"]
        slack_token = os.environ["SLACK_TOKEN"]
        kafka_topic = os.getenv("KAFKA_TOPIC", "nada.nada-soda")
    except KeyError:
        logging.error("Environment variables SODA_CONFIG, SODA_CHECKS_FOLDER, SLACK_CHANNEL and SLACK_TOKEN are all required to run this script")
        exit(1)
    
    soda_checks = NadaSoda(config_path, checks_path, slack_channel, slack_token, kafka_topic)
    try:
        soda_checks.run()
    except:
        logging.error("Running SODA checks failed")
        raise
