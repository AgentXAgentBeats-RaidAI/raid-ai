# RAID-AI: Multilanguage Bug-Fixing Agent Benchmark

## Overview
RAID-AI is a comprehensive benchmark for evaluating AI agents' bug-fixing capabilities across Java, Python, and JavaScript using industry-standard bug datasets.

## Frameworks
- **Defects4J**: 854 real Java bugs from 17 projects
- **BugsInPy**: Python bugs from popular projects
- **BugsJS**: 453 JavaScript bugs from 10 Node.js projects

## Quick Start

### Using Docker (WIP)

### Manual Installation
# RAID-AI Setup Instructions

## Prerequisites
- Ubuntu 24.04 (or similar Linux)
- Java 11
- Python 3.12+
- Node.js
- Git, SVN, Perl

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/AgentXAgentBeats-RaidAI/raid-ai.git
cd raid-ai
```

### 2. Install System Dependencies
```bash
# Java 11
sudo apt install -y openjdk-11-jdk

# Python
sudo apt install -y python3 python3-pip python3-venv

# Node.js
sudo apt install -y nodejs npm

# Other tools
sudo apt install -y git subversion perl cpanminus wget unzip build-essential

# Perl modules
sudo apt install -y libdbi-perl libdbd-csv-perl libjson-perl liburi-perl
```

### 3. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Install Bug Frameworks

#### Defects4J (Java)
```bash
git clone https://github.com/rjust/defects4j.git
cd defects4j
cpanm --installdeps .
./init.sh
export PATH=$PATH:$(pwd)/framework/bin
cd ..
```

#### BugsInPy (Python)
```bash
git clone https://github.com/soarsmu/BugsInPy.git
export PATH=$PATH:$(pwd)/BugsInPy/framework/bin
pip install pytest pytest-cov coverage
```

#### BugsJS (JavaScript)
```bash
git clone https://github.com/BugsJS/bug-dataset.git bugsjs-dataset
git clone https://github.com/BugsJS/docker-environment.git bugsjs-docker
```

### 5. Update Config
Edit `configs/agent_config.yaml` with your paths:
```yaml
paths:
  defects4j: "/your/path/to/defects4j"
  bugsinpy: "/your/path/to/BugsInPy"
  bugsjs: "/your/path/to/bugsjs-dataset"
```

### 6. Test Installation
```bash
source venv/bin/activate
python test_managers.py
```

### 7. Initialize Benchmark
```bash
python -m green_agent.main
```

## Verify
You should see:
- ✅ Java bugs selected
- ✅ Python bugs selected  
- ✅ JavaScript bugs selected (pending fix)
- 📝 Catalog created in `bugs/catalog.json`

## Competition Details
- **Phase 1 Deadline**: December 19, 2025
- **Track**: Software Testing Agent
- **Type**: Green Agent (Benchmark/Evaluator)

## Project Structure
```
raid-ai/
├── green_agent/          # Green agent implementation
│   ├── managers/         # Framework-specific managers
│   ├── evaluator/        # Scoring and evaluation logic
│   └── api/              # A2A protocol interface
├── bugs/                 # Bug catalogs
├── tests/                # Test suite
├── docs/                 # Documentation
├── configs/              # Configuration files
└── scripts/              # Utility scripts
```

## Team
RaidAI

## License
MIT License
