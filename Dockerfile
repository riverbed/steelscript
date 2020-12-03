FROM python:3.9
MAINTAINER Riverbed Technology

# separate out steelhead package to it picks up already installed dependencies
RUN set -ex \
        && buildDeps=' \
                libpcap-dev \
        ' \
        && apt-get update && apt-get install -y $buildDeps --no-install-recommends && rm -rf /var/lib/apt/lists/* \
        \
        && pip install --src /src \
            -e git+https://github.com/riverbed/steelscript#egg=steelscript \
            -e git+https://github.com/riverbed/steelscript-netprofiler#egg=steelscript-netprofiler \
            -e git+https://github.com/riverbed/steelscript-wireshark#egg=steelscript-wireshark \
            -e git+https://github.com/riverbed/steelscript-cmdline#egg=steelscript-cmdline \
            -e git+https://github.com/riverbed/steelscript-scc#egg=steelscript-scc \
            -e git+https://github.com/riverbed/steelscript-appresponse#egg=steelscript-appresponse \
        && pip install Cython \
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
