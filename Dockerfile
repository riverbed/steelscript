# Dockerfile
# version: 24.11.1
#
# Riverbed SteelScript, https://github.com/riverbed/steelscript
#
# Usage
#   
#   # Build
#
#       docker build --tag steelscript:latest -f Dockerfile .
#
#   # Run
#
#       docker run -it --rm steelscript:latest
#

# Use Python image for playground
FROM python:3.13
LABEL org.opencontainers.image.authors="Riverbed Community"
LABEL org.opencontainers.image.source="https://github.com/riverbed/steelscript"
LABEL org.opencontainers.image.title="SteelScript - playground image"
LABEL org.opencontainers.image.version="24.11.1"

# Install tools and deps for build
RUN set -ex && \
        tools=' \
                git \
                nano \
                vim \
        ' && \
        buildDeps=' \
                libpcap-dev \
        ' && \
        apt-get update && \ 
        apt-get upgrade -y && \ 
        apt-get install -y $tools $buildDeps --no-install-recommends && \
        rm -rf /var/lib/apt/lists/*

# Install SteelScript and modules, latest versions 
RUN set -ex && \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir --src /src \
        -e git+https://github.com/riverbed/steelscript#egg=steelscript \
        -e git+https://github.com/riverbed/steelscript-netprofiler#egg=steelscript-netprofiler \
        -e git+https://github.com/riverbed/steelscript-wireshark#egg=steelscript-wireshark \
        -e git+https://github.com/riverbed/steelscript-cmdline#egg=steelscript-cmdline \
        -e git+https://github.com/riverbed/steelscript-scc#egg=steelscript-scc \
        -e git+https://github.com/riverbed/steelscript-appresponse#egg=steelscript-appresponse \
        -e git+https://github.com/riverbed/steelscript-netim#egg=steelscript-netim \
        -e git+https://github.com/riverbed/steelscript-client-accelerator-controller#egg=steelscript-cacontroller \
        -e git+https://github.com/riverbed/steelscript-steelhead#egg=steelscript-steelhead \
        -e git+https://github.com/riverbed/steelscript-packets#egg=steelscript-packets 

# Cleanup
RUN set -ex && \           
        apt-get autoremove && \
        apt-get clean && \
        rm -rf ~/.cache

# Create SteelScript workspace
RUN set -ex && steel mkworkspace -d /steelscript/workspace
WORKDIR /steelscript/workspace

# Configure container startup
CMD ["/bin/bash"]
