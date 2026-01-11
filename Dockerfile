FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    openjdk-11-jdk \
    maven \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# ==================== DEFECTS4J SETUP ====================
# Clone and setup Defects4J (Java bugs)
RUN git clone https://github.com/rjust/defects4j.git /opt/defects4j && \
    cd /opt/defects4j && \
    ./init.sh

ENV PATH="/opt/defects4j/framework/bin:${PATH}"

# Initialize Defects4J (this downloads metadata)
RUN defects4j info -p Lang

# ==================== BUGSINPY SETUP ====================
# Clone and setup BugsInPy (Python bugs)
RUN git clone https://github.com/soarsmu/BugsInPy.git /opt/bugsinpy && \
    cd /opt/bugsinpy && \
    chmod +x framework/bin/*

ENV PATH="/opt/bugsinpy/framework/bin:${PATH}"

# ==================== BUGSJS SETUP ====================
# Clone BugsJS (JavaScript bugs)
RUN git clone https://github.com/BugsJS/BugsJS.git /opt/bugsjs

# ==================== WORKSPACE SETUP ====================
# Create workspace directories
RUN mkdir -p /app/workspace /app/logs /app/data

# Copy application code and configs
COPY green_agent/ /app/green_agent/
COPY tests/ /app/tests/
COPY configs/ /app/configs/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the API server
CMD ["python", "-m", "green_agent.api.a2a_interface"]
