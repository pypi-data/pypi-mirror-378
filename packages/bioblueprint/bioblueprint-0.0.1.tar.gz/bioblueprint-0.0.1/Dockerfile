ARG BIOBLUEPRINT_VER="0.0.1"

FROM google/cloud-sdk:532.0.0

ARG BIOBLUEPRINT_VER

RUN apt-get update \
  && apt-get install -y \
    procps wget tzdata \
    python3 python3-pip python3-setuptools python3-wheel \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/theiagen/theiaphylo/archive/refs/tags/v${BIOBLUEPRINT_VER}.tar.gz \
    && tar -xzf v${BIOBLUEPRINT_VER}.tar.gz \
    && mv theiaphylo-${BIOBLUEPRINT_VER} /theiaphylo \
    && rm v${BIOBLUEPRINT_VER}.tar.gz

RUN python3 -m pip install /bioblueprint/ --break-system-packages

ENV PATH="/bioblueprint/bioblueprint:${PATH}"

WORKDIR /data
