#!/usr/bin/env python

import os
import sys

PROJECTS = [
    ('common', 'SteelScript Common', '..'),
    ('netprofiler', 'SteelScript NetProfiler', '../../steelscript-netprofiler'),
    ('netshark', 'SteelScript NetShark', '../../steelscript-netshark'),
    ('appfwk', 'SteelScript Application Framework', '../../steelscript-appfwk'),
    ('vmconfig', 'SteelScript VM', '../../steelscript-vm-config'),
]

def create_symlinks():
    for proj, title, path in PROJECTS:
        # Create a symlink, ignore common since its part of package
        if proj == 'common':
            continue

        try:
            os.unlink(proj)
        except OSError:
            pass

        src = '{path}/docs'.format(path=path)
        if not os.path.exists(src):
            raise Exception(
                'Could not find related project source tree: %s' % src)

        os.symlink(src, proj)

def write_toc_templates():
    if not os.path.exists('_templates'):
        os.mkdir('_templates')
    for proj, title, path in PROJECTS:
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
    for proj, title, path in PROJECTS:
        tocfile = '%s_toc.html' % proj
        html_sidebars['%s/*' % proj] = \
                             [tocfile, 'relations.html', 'sourcelink.html',
                              'searchbox.html', 'license.html']


def setup_sys_path():
    for proj, title, path in PROJECTS:
        if not os.path.exists(path):
            raise Exception('Could not find related project source tree: %s' % path)
        sys.path.insert(0, os.path.abspath(path))
