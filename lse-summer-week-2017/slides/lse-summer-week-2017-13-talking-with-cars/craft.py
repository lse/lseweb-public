import yaml
import json
from requests import get, post
from jinja2 import Template
from os import system
from os.path import exists, relpath
from sh import git, touch, unzip, rm, mv, glob
from argparse import ArgumentParser


def get_reveal(rjs_dir):
    if exists("reveal.js"):
        return
    REVEAL_REPO = "https://github.com/hakimel/reveal.js/"
    git("clone", REVEAL_REPO, rjs_dir)


def get_highlight(rjs_dir):
    if exists("{}/.hljs".format(rjs_dir)):
        return
    touch("{}/.hljs".format(rjs_dir))
    HIGHLIGHT_URL = "https://highlightjs.org/download/"
    html = get(HIGHLIGHT_URL).text.split("\n")
    lang = [x.strip().split('"')[3] for x in html if "checkbox" in x and "<li>" in x]
    csrf = [x.strip() for x in html if "csrf" in x][0].split("'")[5]
    data = {x: "on" for x in lang}
    data.update({"csrfmiddlewaretoken": csrf})
    headers = {"Referer": "https://highlightjs.org/download/"}
    headers.update({"Cookie": "csrftoken={}".format(csrf)})
    r = post(HIGHLIGHT_URL, data=data, headers=headers, stream=True)
    with open("highlight.zip", "wb") as f:
        for chunk in r.iter_content(4096):
            f.write(chunk)
    unzip("-d", "highlight", "highlight.zip")
    mv("highlight/highlight.pack.js", "{}/plugin/highlight/highlight.js".format(rjs_dir))
    mv(glob("highlight/styles/*"), "{}/lib/css/".format(rjs_dir))
    rm("-r", "highlight", "highlight.zip")


parser = ArgumentParser(description="Create reveal.js slides")
parser.add_argument("action", choices=["all", "env", "pres", "clean"])
parser.add_argument("--rjs", default="reveal.js")
parser.add_argument("--cfg", default="config")
parser.add_argument("--out", default="index.html")
args = parser.parse_args()

if args.action in ["env", "all"]:
    get_reveal(args.rjs)
    get_highlight(args.rjs)
if args.action in ["pres", "all"]:
    meta = yaml.load(open("{}/meta.yaml".format(args.cfg)).read())
    meta["files"] = [open(f).read() for f in meta["files"]]
    meta["markdown"] = meta["separator"].join(meta.pop("files"))
    settings = yaml.load(open("{}/settings.yaml".format(args.cfg)).read())
    settings = {k: json.dumps(v) for k, v in settings.items()}
    meta.update(settings)
    meta["slides"] = meta.pop("markdown").split(meta["separator"])
    html_template = Template(open("{}/template.html".format(args.cfg)).read())
    html = html_template.render(**meta)
    open(args.out, "w").write(html)
if args.action in ["clean"]:
    rm("-r", args.rjs)
