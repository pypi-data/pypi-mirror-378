"""HTML renderering functions."""

__all__ = [
    "create_jinja_env",
    "render_homepage",
    "filter_simple_date",
    "filter_paragraphify",
]

import datetime
import os
import re
from typing import TYPE_CHECKING, Union

import jinja2
import markupsafe

from lander import __version__
from lander.metadata import HighwireMetadata, OpenGraphMetadata

if TYPE_CHECKING:
    from lander.config import Configuration


def create_jinja_env() -> jinja2.Environment:
    """Create a Jinja2 `~jinja2.Environment`.

    Returns
    -------
    env : `jinja2.Environment`
        Jinja2 template rendering environment, configured to use templates in
        ``templates/``.
    """
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(["html"]),
    )
    env.filters["simple_date"] = filter_simple_date
    env.filters["paragraphify"] = filter_paragraphify
    return env


def render_homepage(config: "Configuration", env: jinja2.Environment) -> str:
    """Render the homepage.jinja template with metadata."""
    # Generate metadata
    highwire = HighwireMetadata(config)
    opengraph = OpenGraphMetadata(config)

    template = env.get_template("homepage.jinja")
    rendered_page = template.render(
        config=config,
        lander_version=__version__,
        highwire_metadata=highwire.as_html(),
        opengraph_metadata=opengraph.as_html(),
    )
    return rendered_page


def filter_simple_date(value: Union[datetime.datetime, datetime.date]) -> str:
    """Filter a `datetime.datetime` or `datetime.date` into a
    'YYYY-MM-DD' string.
    """
    return value.strftime("%Y-%m-%d")


def filter_paragraphify(value: str) -> str:
    """Convert text into one or more paragraphs, including <p> tags.

    Based on https://gist.github.com/cemk/1324543
    """
    value = re.sub(r"\r\n|\r|\n", "\n", value)  # Normalize newlines
    paras = re.split("\n{2,}", value)
    paras = ["<p>{0}</p>".format(p) for p in paras if len(p) > 0]
    return markupsafe.Markup("\n\n".join(paras))
