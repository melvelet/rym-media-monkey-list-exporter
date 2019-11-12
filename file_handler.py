from bs4 import BeautifulSoup
import yaml
from collections import OrderedDict


def open_html(file_path):
    with open(file_path, 'r') as stream:
        try:
            soup = BeautifulSoup(stream, features="html.parser")
        except (IOError) as exc:
            print(exc)
    return soup
    

def save_to_yaml(content, file_name):
    with open(f"rym-{file_name}.yml", 'w') as outfile:
        yaml.safe_dump(content, outfile, default_flow_style=False)
        print(f"Results written to rym-{file_name}.yml")


def ordered_dump(data, file_name):
    class OrderedDumper(yaml.SafeDumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    with open(f"rym-{file_name}.yml", 'w') as outfile:
        yaml.dump(data, outfile, OrderedDumper)
        print(f"Results written to rym-{file_name}.yml")