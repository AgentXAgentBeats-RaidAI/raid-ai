# RAID-AI Setup Instructions

Ubuntu 24.04 Linux environment (tested on)

## 1. Clone Repository
```bash
git clone https://github.com/AgentXAgentBeats-RaidAI/raid-ai.git
cd raid-ai
```

## 2. Install System Dependencies
```bash
sudo apt update
sudo apt install -y openjdk-11-jdk openjdk-11-jdk-headless
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y nodejs npm
sudo apt install -y git subversion perl cpanminus wget unzip build-essential
sudo apt install -y libdbi-perl libdbd-csv-perl libjson-perl liburi-perl libtext-csv-perl libtest-simple-perl libstring-interpolate-perl
```

Set Java 11:
```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
```

## 3. Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Install Defects4J (Java)
```bash
git clone https://github.com/rjust/defects4j.git
cd defects4j
cpanm --installdeps .
./init.sh
```

Note: `init.sh` takes 10-30 minutes.
```bash
export PATH=$PATH:$(pwd)/framework/bin
echo "export PATH=\$PATH:$HOME/raid-ai/defects4j/framework/bin" >> ~/.bashrc
defects4j info -p Lang
cd ..
```

## 5. Install BugsInPy (Python)
```bash
git clone https://github.com/soarsmu/BugsInPy.git
export PATH=$PATH:$(pwd)/BugsInPy/framework/bin
echo "export PATH=\$PATH:$HOME/raid-ai/BugsInPy/framework/bin" >> ~/.bashrc
pip install pytest pytest-cov coverage
bugsinpy-info -p youtube-dl
```

## 6. Install BugsJS (JavaScript)
```bash
git clone https://github.com/BugsJS/bug-dataset.git bugsjs-dataset
git clone https://github.com/BugsJS/docker-environment.git bugsjs-docker
ls bugsjs-dataset/Projects/
```

## 7. Reload Shell
```bash
source ~/.bashrc
source venv/bin/activate
```

## 8. Verify Installation
```bash
cd ~/raid-ai
source venv/bin/activate
python test_managers.py
```

## 9. Initialize Benchmark
```bash
python -m green_agent.main
```

This creates `bugs/catalog.json` with 90 selected bugs (30 per language).

## 10. Run API (Optional)
```bash
python -m green_agent.api.a2a_interface
```

Test in another terminal:
```bash
curl http://localhost:8000/benchmark/info
```

## Final Directory Structure
```
raid-ai/
├── defects4j/
├── BugsInPy/
├── bugsjs-dataset/
├── green_agent/
├── bugs/
│   └── catalog.json
├── venv/
├── test_managers.py
└── requirements.txt
```

## Troubleshooting

**Command not found errors:**
```bash
export PATH=$PATH:$HOME/raid-ai/defects4j/framework/bin
export PATH=$PATH:$HOME/raid-ai/BugsInPy/framework/bin
source ~/.bashrc
```

**ModuleNotFoundError:**
```bash
cd ~/raid-ai
source venv/bin/activate
pip install -e .
```

**Perl module errors:**
```bash
sudo apt install -y libdbi-perl libdbd-csv-perl libjson-perl
```

## Quick Test
```bash
cd ~/raid-ai
source venv/bin/activate
defects4j info -p Chart
bugsinpy-info -p keras
python test_managers.py
python -m green_agent.main
```

## Time Required
Setup takes 30-60 minutes depending on internet speed. Most time spent on Defects4J initialization.