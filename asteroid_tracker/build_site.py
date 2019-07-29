import argparse
from dataclasses import dataclass
from datetime import datetime
import os.path
from pathlib import Path
import sys
import shutil

import yaml
import jinja2
import requests

def current_year():
    return datetime.now().strftime("%Y")

@dataclass
class Target:
    pk: int
    template: int
    preview_image: str
    teaser: str = ""

    def preview_image_name(self):
        """
        Return the filename for the preview image to be copied to the static
        output directory
        """
        suffix = Path(self.preview_image).suffix
        return f"{self.pk}{suffix}"

@dataclass
class Page:
    name: str
    template: jinja2.Template
    context: dict

class SiteBuilder:
    def __init__(self, config_path):
        config = self.parse_config(config_path)
        self.base_url = config["tom_education_url"]
        self.targets = [Target(**info) for info in config["targets"]]

        # Remove trailing slash from base URL so that JS client can always
        # append API url to base without worrying about double /
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        # Construct Jinja environment
        here = Path(os.path.dirname(__file__))
        template_dir = here / "templates"
        self.static_dir = here / "static"
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        self.env.globals["current_year"] = current_year()

    def parse_config(self, path):
        return yaml.safe_load(path.read_text())

    def build_site(self, outdir):
        outdir.mkdir(exist_ok=True)

        for page in self.get_pages():
            dest_dir = outdir / page.name
            dest_dir.mkdir(exist_ok=True)
            dest_file = dest_dir / "index.html"
            dest_file.write_text(page.template.render(**page.context))

        # Copy static files
        out_static = outdir / "static"
        if out_static.exists():
            shutil.rmtree(out_static)
        shutil.copytree(self.static_dir, out_static)
        # Copy target preview images
        preview_images = out_static / "previews"
        preview_images.mkdir(exist_ok=True)
        for target in self.targets:
            dest = preview_images / target.preview_image_name()
            shutil.copyfile(target.preview_image, dest)

    def get_pages(self):
        home_context = {"targets": []}

        # Create a page for each target
        target_template = self.env.get_template("asteroid.html.tmpl")
        for target in self.targets:
            api_url = f"/api/target/{target.pk}/"
            response = requests.get(self.base_url + api_url)
            details = response.json()

            identifier = details["target"]["identifier"]
            context = {
                "base_url": self.base_url,
                "api_url": api_url
            }
            yield Page(name=identifier, template=target_template, context=context)

            # Add this target to the list to be shown on the home page
            home_context["targets"].append({
                "url": f"/{identifier}",
                "name": details["target"]["name"],
                "image_name": target.preview_image_name(),
                "teaser": target.teaser
            })

        # Home page
        yield Page(
            name="",
            template=self.env.get_template("home.html.tmpl"),
            context=home_context
        )

def main():
    parser = argparse.ArgumentParser(
        description="Create a static site to view and create timelapses of "
                    "asteroids using an instance of the TOM Toolkit"
    )
    parser.add_argument(
        "config",
        help="Path to YAML config file",
        type=Path
    )
    parser.add_argument(
        "output_directory",
        help="Directory to write static site to",
        type=Path
    )
    args = parser.parse_args(sys.argv[1:])

    builder = SiteBuilder(args.config)
    builder.build_site(args.output_directory)

if __name__ == "__main__":
    main()
