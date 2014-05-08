#!/usr/bin/env python

import os
import sys

PROJECTS = {
    'common'      : 'SteelScript Common',
    'netprofiler' : 'SteelScript NetProfiler',
    'netshark'    : 'SteelScript NetShark',
}


def create_symlinks():
    for proj, title in PROJECTS.iteritems():
        # Create a symlink, ignore common since its part of package
        try:
            if proj != 'common':
                os.unlink(proj)
        except OSError:
            pass

        src = '../../steelscript-{proj}/docs'.format(proj=proj)
        if not os.path.exists(src):
            raise Exception('Could not find related project source tree: %s' % src)

        os.symlink(src, proj)


def write_toc_templates():
    for proj, title in PROJECTS.iteritems():
        # Write a custom TOC template file
        tocfile = '%s_toc.html' % proj
        template_tocfile = '_templates/%s' % tocfile
        if not os.path.exists(template_tocfile):
            with open(template_tocfile, 'w') as f:
                f.write("""{{%- if display_toc %}}
  <h3><a href="{{{{ pathto('{proj}/index.html', 1) }}}}">{{{{ _('{title}') }}}}</a></h3>
  {{{{ toc }}}}
{{%- endif %}}""".format(proj=proj, title=title))


def setup_html_sidebards(html_sidebars):
    for proj in PROJECTS.keys():
        tocfile = '%s_toc.html' % proj
        html_sidebars['%s/*' % proj] = \
                             [tocfile, 'relations.html',
                              'sourcelink.html', 'searchbox.html']


def setup_sys_path():
    for proj, title in PROJECTS.iteritems():
        src = '../../steelscript-%s' % proj
        if not os.path.exists(src):
            raise Exception('Could not find related project source tree: %s' % src)
        sys.path.insert(0, os.path.abspath(src))


if __name__ == '__main__':
    create_symlinks()
    write_toc_templates()
