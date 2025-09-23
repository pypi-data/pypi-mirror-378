from lxml import etree
from tomlkit import table

from dexpi.specificator.formatter import Formatter


def get_default_config():
    config = table()
    config.add('pretty_print', True)
    return config

def make(model_by_name, metadata, out_dir, config):
    from pnb.mcl.io.xmi import XmiWriter
    out_dir.mkdir(parents=True, exist_ok=True)
    
    from pnb.mcl.metamodel.standard import ModelSet
    
    model_set = ModelSet()
    for model in model_by_name.values():
        model_set.add(model)
    
    etree.ElementTree(XmiWriter(model_set).root).write(
        out_dir / 'model.xmi', encoding='utf-8', pretty_print=config['pretty_print'])
   # etree.ElementTree(XmiWriter(model_by_name, mode='modelio').root).write(
   #     out_dir / 'model (Modelio).xmi', encoding='utf-8', pretty_print=config['pretty_print'])

FORMATTER = Formatter(
    'xmi', get_default_config, make)
