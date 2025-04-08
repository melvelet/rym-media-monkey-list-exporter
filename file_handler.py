import json

from bs4 import BeautifulSoup
import yaml
from collections import OrderedDict


def open_html(file_path):
    with open(file_path, 'r', encoding="utf-8") as stream:
        try:
            soup = BeautifulSoup(stream, features="html.parser")
        except IOError as exc:
            print(exc)
    return soup


def save_to_yaml(content, file_name):
    with open(f"{file_name}.yml", 'w') as outfile:
        yaml.safe_dump(content, outfile, default_flow_style=False)
        print(f"Results written to {file_name}.yml")


def open_yaml(file_name):
    with open(f"{file_name}.yml") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def open_json(file_name):
    try:
        with open(file_name) as f:
            return json.load(f)
    except FileNotFoundError as exc:
        print(f"File {file_name} not found, starting new RYM-ID-in-MM dictionary")
        return dict()


def save_to_json(content, file_name):
    with open(file_name, 'w+') as f:
        return json.dump(content, f)


def ordered_dump(data, file_name):
    class OrderedDumper(yaml.SafeDumper):
        pass

    def __dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, __dict_representer)
    with open(f"{file_name}.yml", 'w') as outfile:
        yaml.dump(data, outfile, OrderedDumper)
        print(f"Results written to rym-{file_name}.yml")
