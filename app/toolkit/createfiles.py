"""
Copyright 2019-2024 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/ssp-toolkit#copyright.


Given a YAML file and path to directory of template files, this tool
generates markdown files, replicating the directory structure in the template
directory. It uses the https://github.com/CivicActions/secrender tool for
variable replacement.
"""

from pathlib import Path

from app.projects.file_manager import FileManager
from app.toolkit.base.config import Config
from app.toolkit.base.secrender import secrender
from app.toolkit.base.ssptoolkit import find_toc_tag


def render(templates: list, project_path: Path, config: Config, manager: FileManager):
    for template in templates:
        template_path = project_path.joinpath("templates").joinpath(template)
        template_parents = Path(template).parent
        new_file_name = (
            Path(template_path.name).stem
            if template_path.suffix == ".j2"
            else template_path.name
        )
        new_file = Path("rendered").joinpath(template_parents).joinpath(new_file_name)
        to_render = secrender(
            template_path=template_path.absolute().as_posix(),
            template_args=config.config,
        )
        manager.write_file(file_path=new_file, file_body=to_render)

        find_toc_tag(file=str(project_path.joinpath(new_file).absolute()))
