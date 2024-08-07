# Mongo-DB

## Routes

- **GET**: `/` : Checks API status.
- **GET**: `/api/mongo` : Checks API status.
- **POST**: `/api/mongo/create_document` : Creates a document.
- **GET**: `/api/mongo/get_document/<collection_name>/<doc_id>` : Gets a document by ID.
- **DELETE**: `/api/mongo/delete_document/<collection_name>/<doc_id>` : Deletes a document by ID.
- **GET**: `/api/mongo/get_all_documents/<collection_name>` : Gets all documents in a collection.
- **POST**: `/api/mongo/update_document` : Updates a document by ID.

## Getting Started

### Install `mongo-db` on Linux environment

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org

ls /etc/init.d/mongod

sudo nano /etc/init.d/mongod
```

- `copy-paste` this content
```bash
#!/bin/bash
### BEGIN INIT INFO
# Provides:          mongod
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start MongoDB at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

. /lib/lsb/init-functions

DAEMON=/usr/bin/mongod
DAEMON_NAME=mongod
DAEMON_OPTS="--config /etc/mongod.conf"

PIDFILE=/var/run/$DAEMON_NAME.pid

case "$1" in
    start)
        log_daemon_msg "Starting system $DAEMON_NAME Daemon"
        start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- $DAEMON_OPTS
        log_end_msg $?
        ;;
    stop)
        log_daemon_msg "Stopping system $DAEMON_NAME Daemon"
        start-stop-daemon --stop --quiet --pidfile $PIDFILE
        log_end_msg $?
        ;;
    restart|reload|force-reload)
        $0 stop
        $0 start
        ;;
    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;
    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;
esac
exit 0
```
- Finalize the installation and start the service
```bash
sudo chmod +x /etc/init.d/mongod

sudo update-rc.d mongod defaults

sudo service mongod start
```

### Getting code-ready

```bash
pip insall pymongo flask python-dotenv
```
