# neo4j 

## Start Service

```bash
sudo service neo4j start
sudo service neo4j enable
sudo service neo4j status
```

## Getting Started

### Install `neo4j` on Linux environment

```bash
sudo apt-get update

sudo apt-get upgrade

wget -qO - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb http://debian.neo4j.com stable 4.0' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update

sudo apt update

sudo apt install neo4j

sudo apt install openjdk-11-jdk
```

### Setup neo4j password

```bash
sudo service neo4j start
sudo service neo4j enable
sudo service neo4j status

cypher-shell -u neo4j -p neo4j
```