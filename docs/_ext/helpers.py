#!/usr/bin/env python

import os
import sys
from importlib.metadata import distribution


PROJECTS = [
    ['common', 'steelscript', 'SteelScript Common', '..'],
    ['netprofiler', 'steelscript.netprofiler', 'SteelScript NetProfiler', '../../steelscript-netprofiler'],
    ['appresponse', 'steelscript.appresponse', 'SteelScript AppResponse', '../../steelscript-appresponse'],
    ['steelhead', 'steelscript.steelhead', 'SteelScript SteelHead', '../../steelscript-steelhead'],
    ['scc', 'steelscript.scc', 'SteelScript SteelCentral Controller', '../../steelscript-scc'],
    ['cmdline', 'steelscript.cmdline', 'SteelScript Command Line', '../../steelscript-cmdline'],
    ['reschema', 'reschema', 'Reschema', '../../reschema'],
    ['sleepwalker', 'sleepwalker', 'Sleepwalker', '../../sleepwalker']
]

for p in PROJECTS:
    proj, pkg, title, path = p

    if proj == 'common':
        continue

    dist = distribution(pkg)
    location = str(dist.locate_file(""))
    if location != os.path.abspath(path):
        p[3] = location


def create_symlinks():
    for proj, pkg, title, path in PROJECTS:
        # Create a symlink, ignore common since its part of package
        if proj == 'common':
            continue

        try:
            os.unlink(proj)
        except OSError:
            pass

        src = '{path}/docs'.format(path=path)
        if os.path.exists(src):
            os.symlink(src, proj)
        else:
            from IPython import embed;embed()
            raise Exception(
                'Could not find related project source tree: %s' % src)


def write_toc_templates():
    if not os.path.exists('_templates'):
        os.mkdir('_templates')
    for proj, pkg, title, path in PROJECTS:
        # Write a custom TOC template file
        tocfile = '%s_toc.html' % proj
        template_tocfile = '_templates/%s' % tocfile
        if not os.path.exists(template_tocfile):
            with open(template_tocfile, 'w') as f:
                f.write("""{{%- if display_toc %}}
  <h3><a href="{{{{ pathto('{proj}/overview.html', 1) }}}}">{{{{ _('{title}') }}}}</a></h3>
  {{{{ toc }}}}
{{%- endif %}}""".format(proj=proj, title=title))


def setup_html_sidebards(html_sidebars):
    for proj, pkg, title, path in PROJECTS:
        tocfile = '%s_toc.html' % proj
        html_sidebars['%s/*' % proj] = \
                             [tocfile, 'relations.html', 'sourcelink.html',
                              'searchbox.html', 'license.html']


def setup_sys_path():
    for proj, pkg, title, path in PROJECTS:
        if not os.path.exists(path):
            raise Exception('Could not find related project source tree: %s' % path)
        sys.path.insert(0, os.path.abspath(path))
