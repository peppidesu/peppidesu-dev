from lib.runners_sh_website.solstice import *
from os import path
import os
from itertools import chain

pages_path = "pages"
blog_path = path.join(pages_path, "blog")


def generate_path_parts(p):
    path_parts = []
    acc = "/"
    for part in path.split(p):
        acc = path.join(acc, part)
        path_parts.append((part, acc))
    if path_parts[0][0] == "":
        del path_parts[0]
    return path_parts


def build_blog(ssg: SiteGenerator) -> list[dict]:
    all_posts = []

    for root, dirs, files in os.walk(blog_path):
        output_root = path.relpath(root, pages_path)
        posts = []
        for file in files:
            name, ext = path.splitext(file)
            if ext not in [".md"]:
                continue

            src_path = path.join(root, file)
            dist_path = path.join(output_root, name + ".html")

            pg = MarkdownPage(ssg, "blog/post.jinja", src_path, dist_path)
            pg.set_params(path_parts=generate_path_parts(output_root))
            if not pg.meta.get("hidden", False):
                posts.append(
                    pg.meta | {"url": "/" + dist_path.removesuffix(".html")}
                )

            pg.build()

        all_posts += posts
        if output_root != blog_path:
            pg = Page(
                ssg,
                "blog/index.jinja",
                path.join(output_root, "index.html"),
            )
            pg.set_params(
                posts=posts, path_parts=generate_path_parts(output_root)
            )
            pg.build()

    all_posts.sort(key=lambda x: x["date"], reverse=True)
    ssg.page(
        "blog/index.jinja",
        posts=all_posts,
        path_parts=generate_path_parts("blog"),
    )
    return all_posts


ssg = SiteGenerator()


@cli.entrypoint(ssg)
def build():
    ssg.copy("public")

    posts = build_blog(ssg)
    index = Page(ssg, "index.jinja")

    index_content, _, _ = ssg.load_md("pages/index.md")
    index.set_params(content=index_content)
    index.set_params(posts=posts[:3])
    index.build()
