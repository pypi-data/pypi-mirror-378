import itertools
from pathlib import Path
from typing import Any

import attrs
import cytoolz as toolz
import git
import jinja2
import platformdirs
from loguru import logger

from liblaf import grapes
from liblaf.tangerine import plugin, utils

from .constants import TANGERINE_END, TANGERINE_START
from .template import Template

type Segment = str | Template


def _load_copier_answers() -> dict[str, Any]:
    try:
        repo = git.Repo(search_parent_directories=True)
        cwd = Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        cwd = Path()
    answers: dict[str, Any] = {}
    for file in itertools.chain(
        cwd.rglob(".copier-answers.*.yaml"),
        cwd.rglob(".copier-answers.*.yml"),
        cwd.rglob(".copier-answers.yaml"),
        cwd.rglob(".copier-answers.yml"),
    ):
        answers.update(grapes.load(file))
    answers = toolz.keyfilter(lambda k: not k.startswith("_"), answers)
    return answers


def _default_environment() -> jinja2.Environment:
    loaders: list[jinja2.BaseLoader] = []
    dirs: platformdirs.AppDirs = utils.app_dirs()
    for config_dir in dirs.iter_config_paths():
        search_path: Path = config_dir / "templates"
        if not search_path.is_dir():
            continue
        loaders.append(jinja2.FileSystemLoader(search_path))
    loaders.append(jinja2.PackageLoader("liblaf.tangerine"))
    env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        autoescape=jinja2.select_autoescape(),
        loader=jinja2.ChoiceLoader(loaders),
        enable_async=True,
    )
    env.filters["strip_emoji"] = plugin.strip_emoji
    env.globals["github_description"] = plugin.github_description
    env.globals.update(_load_copier_answers())
    return env


@attrs.define
class Environment:
    jinja: jinja2.Environment = attrs.field(factory=_default_environment)

    def parse(self, text: str) -> list[Segment]:
        lines: list[str] = text.splitlines()
        segments: list[Segment] = []
        in_template: bool = False
        template_lines: list[str] = []
        for line in lines:
            if in_template:
                template_lines.append(line)
                if TANGERINE_END in line:
                    segments.append(Template.from_lines(template_lines))
                    in_template = False
                    template_lines = []
            elif TANGERINE_START in line:
                in_template = True
                template_lines.append(line)
            else:
                segments.append(line)
        return segments

    async def render(self, segments: list[Segment], **kwargs: str) -> str:
        lines: list[str] = []
        for segment in segments:
            if isinstance(segment, Template):
                lines.append(await self.render_template(segment, **kwargs))
            else:
                lines.append(segment)
        text: str = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
        return text

    async def render_template(self, template: Template, **kwargs: str) -> str:
        try:
            template_jinja: jinja2.Template = self.jinja.get_template(template.name)
        except jinja2.TemplateNotFound as err:
            for template_name in err.templates:
                logger.warning("Template not found: {}", template_name)
            return "\n".join(template.lines)
        kwargs = toolz.merge(template.context, kwargs)
        rendered: str = await template_jinja.render_async(kwargs)
        rendered = rendered.strip()
        lines: list[str] = rendered.splitlines()
        rendered = "\n".join(lines).strip()
        rendered = template.lines[0] + "\n" + rendered + "\n" + template.lines[-1]
        return rendered
