from tomlkit import table
from lxml import etree

from dexpi.specificator.formatter import Formatter

def get_default_config():
    config = table()
    config.add('pretty_print', True)
    return config

def make(model_by_name, metadata, out_dir, config):
    out_dir.mkdir(parents=True, exist_ok=True)
    from pnb.mcl.io.xml import XmlExporter
    for name, model in model_by_name.items():
        xml = XmlExporter(
            model,
            metadata,
            'DexpiMeta',
            'http://www.dexpi.org/specification/2.0/MetaData').xml
        out_path = out_dir / f'{name}.xml'
        etree.ElementTree(xml).write(
            out_path, encoding='utf-8', pretty_print=config['pretty_print'])

FORMATTER = Formatter(
    'xml', get_default_config, make)
