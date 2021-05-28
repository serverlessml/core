"""Test lambda."""

import json
import logging
from typing import Any, Dict

from pythonjsonlogger.jsonlogger import JsonFormatter


class LogsFormatter(JsonFormatter):
    """``LogsFormatter`` defines the logs formatter class."""

    def __init__(self, request_id: str = None) -> None:
        """Instantiates `LogsFormatter`.

        Args:
            request_id: Trigger message ID.
        """
        fmt = "%(asctime)s %(levelname)s %(run_id)s %(lineno)d %(message)s"
        if not request_id:
            fmt = "%(asctime)s %(levelname)s %(request_id)s %(run_id)s %(lineno)d %(message)s"

        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

        self.request_id = request_id

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_record["request_id"] = self.request_id

        if isinstance(message_dict.get("message"), dict):
            log_record.pop("message")
            log_record.update(message_dict)

        if not message_dict.get("run_id"):
            log_record.pop("run_id")


def get_logger(request_id: str, name: str = __name__) -> logging.Logger:
    """Sets up the logger.

    Args:
        request_id: Trigger message ID.
        name: Logger instance name.

    Returns:
        Logger.
    """
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(LogsFormatter(request_id=request_id))
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    for hdl in logger.handlers:
        logger.removeHandler(hdl)

    logger.addHandler(json_handler)
    return logger


def run(event: Dict[str, Any], context: Any) -> str:  # pylint: disable=unused-argument
    """Contains the end-to-end logic to run pipelines.

    Args:
        event: AWS lambda event object.
        context: AWS lambda context.
    """
    log = get_logger(context.aws_request_id)

    record: Dict[str, Any] = event["Records"][0]["Sns"]
    payload: Dict[str, Any] = json.loads(record["Message"])

    project_id = payload.get("project_id")
    run_id = payload.get("run_id")

    log.error({
        "run_id": run_id,
        "message": f"""Project ID: {payload.get("project_id")}"""
    })

    # log.info("test")

    return project_id


# class Context:
#     aws_request_id: str


# ctx = Context()
# ctx.aws_request_id = "test"

# run(
#     event={
#         "Records": [
#             {
#                 "EventSource": "aws:sns",
#                 "EventVersion": "1.0",
#                 "EventSubscriptionArn": "arn:aws:sns:eu-west-1:123456789012:trigger_0cba82ff-9790-454d-b7b9-22570e7ba28c-train",
#                 "Sns": {
#                     "Type": "Notification",
#                     "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
#                     "TopicArn": "arn:aws:sns:eu-west-1:123456789012:trigger_0cba82ff-9790-454d-b7b9-22570e7ba28c-train",
#                     "Message": '{"project_id": "0cba82ff-9790-454d-b7b9-22570e7ba28c", "code_hash": "8c2f3d3c5dd853231c7429b099347d13c8bb2c37", "run_id": "c77d0a32-2b29-47f6-9ac5-67a21f7953b9", "pipeline_config": {"data": {"location": {"source": "s3://test/train.csv"}, "prep_config": {}}, "model": {"hyperparameters": {}, "version": "test.v1"}}}',
#                     "Timestamp": "1970-01-01T00:00:00.000Z",
#                     "SignatureVersion": "1",
#                     "Signature": "EXAMPLE",
#                     "SigningCertUrl": "EXAMPLE",
#                     "UnsubscribeUrl": "EXAMPLE",
#                     "MessageAttributes": {
#                         "Test": {"Type": "String", "Value": "TestString"},
#                         "TestBinary": {"Type": "Binary", "Value": "TestBinary"},
#                     },
#                 },
#             }
#         ]
#     },
#     context=ctx,
# )
