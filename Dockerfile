FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

# dependencies
RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    git subversion \
    perl-base cpanminus wget unzip \
    python3 python3-pip python3-dev python3-venv \
    nodejs npm \
    build-essential \
    curl vim nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /workspace
WORKDIR /workspace

RUN echo "Installing Defects4J..." && \
    git clone https://github.com/rjust/defects4j.git && \
    cd defects4j && \
    cpanm --installdeps . && \
    ./init.sh

ENV D4J_HOME=/workspace/defects4j
ENV PATH=$PATH:$D4J_HOME/framework/bin

RUN echo "Installing BugsInPy..." && \
    git clone https://github.com/soarsmu/BugsInPy.git && \
    pip3 install --no-cache-dir pytest pytest-cov coverage

ENV BUGSINPY_HOME=/workspace/BugsInPy
ENV PATH=$PATH:$BUGSINPY_HOME/framework/bin


RUN echo "Installing BugsJS..." && \
    git clone https://github.com/BugsJS/bug-dataset.git bugsjs-dataset && \
    git clone https://github.com/BugsJS/docker-environment.git bugsjs-docker

RUN cd bugsjs-docker && npm install -g . || echo "BugsJS CLI optional"

ENV BUGSJS_HOME=/workspace/bugsjs-dataset

RUN pip3 install --no-cache-dir \
    requests \
    fastapi \
    uvicorn \
    pydantic \
    pytest \
    pyyaml \
    python-dotenv \
    click


RUN mkdir -p /workspace/project

WORKDIR /workspace/project

RUN echo "=== Verification ===" && \
    java -version && \
    python3 --version && \
    node --version && \
    defects4j info -p Lang | head -n 5 && \
    echo "=== Setup Complete ==="

CMD ["/bin/bash"]
