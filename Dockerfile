FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies INCLUDING PERL MODULES (with retry logic)
RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        openjdk-11-jdk \
        maven \
        vim \
        cpanminus

# Install Perl modules required by Defects4J
RUN cpanm --notest String::Interpolate

# clean up
RUN rm -rf /var/lib/apt/lists/*

# Install Node.js 18 (with retry logic)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy and install Python requirements
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --default-timeout=100 --retries=10 -r /app/requirements.txt

# ==================== DEFECTS4J SETUP ====================
RUN git clone https://github.com/rjust/defects4j.git /opt/defects4j && \
    cd /opt/defects4j && \
    cpanm --notest --installdeps . && \
    ./init.sh

ENV PATH="/opt/defects4j/framework/bin:${PATH}"
RUN defects4j info -p Lang

# ==================== BUGSINPY SETUP ====================
RUN git clone https://github.com/soarsmu/BugsInPy.git /opt/bugsinpy && \
    cd /opt/bugsinpy && \
    chmod +x framework/bin/*

ENV PATH="/opt/bugsinpy/framework/bin:${PATH}"

# ==================== BUGSJS SETUP ====================
RUN git clone https://github.com/BugsJS/bug-dataset.git /opt/bugsjs

# ==================== WORKSPACE SETUP ====================
RUN mkdir -p /app/workspace /app/logs /app/data /app/bugs

# Copy application code
COPY green_agent/ /app/green_agent/
COPY tests/ /app/tests/
COPY configs/ /app/configs/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "green_agent.api.a2a_interface"]