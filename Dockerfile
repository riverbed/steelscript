FROM python:2.7
MAINTAINER Riverbed Technology

# separate out steelhead package to it picks up already installed dependencies
RUN set -ex \
        && pip install --src /src \
            -e git+https://github.com/riverbed/steelscript#egg=steelscript \
            -e git+https://github.com/riverbed/steelscript-netprofiler#egg=steelscript-netprofiler \
            -e git+https://github.com/riverbed/steelscript-netshark#egg=steelscript-netshark \
            -e git+https://github.com/riverbed/steelscript-wireshark#egg=steelscript-wireshark \
            -e git+https://github.com/riverbed/steelscript-cmdline#egg=steelscript-cmdline \
            -e git+https://github.com/riverbed/steelscript-scc#egg=steelscript-scc \
            -e git+https://github.com/riverbed/steelscript-appresponse#egg=steelscript-appresponse \
        && pip install --src /src \
            -e git+https://github.com/riverbed/steelscript-steelhead#egg=steelscript-steelhead \
            -e git+https://github.com/riverbed/steelscript-packets.git@master#egg=steelscript-packets \
        && rm -f /src/pip-delete-this-directory.txt \
        && rm -rf ~/.cache

RUN set -ex \
        && steel mkworkspace -d /root/steelscript-workspace

WORKDIR /root/steelscript-workspace

# Configure container startup
CMD ["/bin/bash"]
