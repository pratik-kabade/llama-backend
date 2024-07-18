# LLAMA-Backend

## Installation

### Python Libraries
```bash
pip install requirements.txt
```

### neo4j 
```bash
sudo apt-get update
sudo apt-get upgrade
wget -qO - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb http://debian.neo4j.com stable 4.0' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt update
sudo apt install openjdk-11-jdk
sudo service neo4j start
sudo service neo4j enable
sudo service neo4j status
cypher-shell -u neo4j -p neo4j
```

### Ollama 
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama run llama2
```

## Additional Commands
```bash
sudo nano /etc/neo4j/neo4j.conf
```

```bash
netstat -tuln | grep 7474
```