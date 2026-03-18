import json
import os
from base64 import b64decode
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml
from jinja2 import Template

from documents import docx_fill_template
from mail import mail_send_documents
from minio_save import save_to_minio

TZ_MSK = ZoneInfo("Europe/Moscow")


def handler(event: dict, context: dict):
    """
    Основной обработчик событий - внешних http запросов
    """
    body = b64decode(event["body"]).decode("utf-8") if event["isBase64Encoded"] else event["body"]
    form_answer: dict = json.loads(body)
    print(f"FORM ANSWER:\n{json.dumps(form_answer)}")

    with open("substitute.yaml", "r") as substitute_file:
        substitute: dict = yaml.safe_load(substitute_file)

    form_data: dict = form_answer["answer"]["data"]

    ###################################
    # Подготовка основных данных
    ###################################
    created = form_answer["answer"]["created"]
    created_dt = datetime.fromisoformat(created).astimezone(TZ_MSK).strftime("%Y_%m%d_%H%M%S")
    issue_main = {
        "form_name": form_answer["form_name"],
        "created": created,
        "created_dt": created_dt,
    }

    ###################################
    # Подготовка данных о родителе
    ###################################
    issue_parent = {
        key: _safe_form_value(key, value)
        for key, value in form_data.items()
        if not _key_is_answer_group(key)
    }

    ###################################
    # Подготовка данных о детях
    ###################################
    issues_children = [
        {key: _safe_form_value(key, value) for key, value in child.items()}
        for key, value in form_data.items()
        if _key_is_answer_group(key)
        for child in value["value"]
    ]

    ###################################
    # Подготовка данных для шаблонов
    ###################################
    issues = []
    for issue_child in issues_children:
        issue = issue_main | issue_parent | issue_child

        # Подстановка данных из файла substitute.yaml
        for key, value in substitute.items():
            issue[key] = Template(value).render(issue)
        issues.append(issue)

    ###################################
    # Генерация и высылка документов
    ###################################
    for issue in issues:
        issue: dict
        variables = {f"{'{'}{'{'} {key} {'}'}{'}'}": f"{value}" for key, value in issue.items()}
        template_files = os.listdir("templates")
        documents = {
            filename: docx_fill_template(f"templates/{filename}", variables)
            for filename in template_files
            if filename.endswith(".docx")
        }
        for filename in template_files:
            if filename.endswith(".pdf"):
                with open(f"templates/{filename}", "rb") as file:
                    documents |= {filename: file.read()}
        mail_send_documents(issue, documents)
        save_to_minio(issue, documents)

    return {"statusCode": 200}


def _key_is_answer_group(key: str) -> bool:
    """
    Проверка того, что заданный ключ является группой ответов
    """
    return key.startswith("answer_group")


def _safe_form_value(key: str, value) -> str:
    """
    Безопасное получение данных формы - получает данные по формату и меняет формат записи даты
    """
    if key.endswith("date"):
        datetime_obj = datetime.strptime(value["value"], "%Y-%m-%d")
        return datetime_obj.strftime("%d.%m.%Y")
    return value["value"]
