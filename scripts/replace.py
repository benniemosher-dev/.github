#!/bin/bash

import pathlib
import re
import os
import argparse
from string import Template

parser = argparse.ArgumentParser(description='Short sample app')
parser.add_argument('--path', action='store', dest='path', default='./')
parser.add_argument('--format', action='store', dest='format', default='table')
args = parser.parse_args()

root = pathlib.Path(args.path).resolve()
infracost_command = Template(
    'infracost breakdown --format=$format --no-color --path=$path'
)


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r'<!\-\- {}_starts \-\->.*<!\-\- {}_ends \-\->'.format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = '\n{}\n'.format(chunk)
    chunk = '<!-- {}_starts -->\n```{}```\n<!-- {}_ends -->'.format(
        marker, chunk, marker
    )
    return r.sub(chunk, content)


if __name__ == '__main__':
    output_stream = os.popen(
        infracost_command.substitute(path=args.path, format=args.format)
    )

    readme = root / 'README.md'
    readme_contents = readme.open().read()
    rewritten = replace_chunk(readme_contents, 'cost', output_stream.read())

    readme.open('w').write(rewritten)
