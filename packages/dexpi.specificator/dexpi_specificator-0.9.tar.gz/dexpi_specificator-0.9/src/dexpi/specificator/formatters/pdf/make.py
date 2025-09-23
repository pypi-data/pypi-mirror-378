import pathlib
import shutil
import subprocess
import sys

from pnb.mcl.io.xml import XmlExporter

from lxml import etree

SCRIPTS_DIR = pathlib.Path(sys.executable).parent.resolve()
SPHINX_BUILD_PATH = SCRIPTS_DIR / 'sphinx-build'


def make(model_by_name, metadata, out_dir, config):

    original_sphinx_project_dir = pathlib.Path(config['sphinx_project'])
    if not original_sphinx_project_dir.is_dir():
        raise Exception() # TODO
    try:
        shutil.rmtree(out_dir)
    except FileNotFoundError:
        pass

    sphinx_project_dir = out_dir / '.sphinx'
    shutil.copytree(original_sphinx_project_dir, sphinx_project_dir)

    model_dir = sphinx_project_dir / '_models'
    model_dir.mkdir(parents=True)
    
    # TODO: run sphix directly if supported by theme.

    if 1:
        for model in model_by_name.values():
            etree.ElementTree(XmlExporter(model).xml).write(model_dir / f'{model.name}.xml')
        metadata.write(model_dir / 'metadata')
        sphinx_process = subprocess.Popen([
            SPHINX_BUILD_PATH, '-M', 'latex', sphinx_project_dir, out_dir, '-v'])
        sphinx_process.wait()
        
    else:
        from sphinx.cmd.build import main
        from ... import sphinx_ext
        with sphinx_ext.model_by_name_context(model_by_name):
            main(['-M', 'latex', str(sphinx_project_dir), str(out_dir), '-v'])
 
    # TODO: get tex filename - from config?
    # TODO: check labels changed before re-running
    for nr in range(3):
        print(f'* LaTeX run {nr} *')
        subprocess.call(
            ['pdflatex', 'flexpiminus.tex'],
            cwd=out_dir / 'latex')
