# Database Setup Guide for AI Agents Orchestration Project

This guide provides a step-by-step process to set up SQL Server 2019 on Docker and restore the **AdventureWorks2019** database for local use.

## **Table of Contents**
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup SQL Server on Docker](#setup-sql-server-on-docker)
- [Install sqlcmd](#install-sqlcmd)
- [Copy .bak File to the Container](#copy-bak-file-to-the-container)
- [Restore Database from .bak File](#restore-database-from-bak-file)
- [Verify the Restoration](#verify-the-restoration)

---

## **Overview**

This document provides a detailed setup to help you run SQL Server 2019 in a Docker container, install `sqlcmd` for SQL interactions, and restore the **AdventureWorks2019** database from a `.bak` file.

## **Prerequisites**
- Docker should be installed and running on your machine.
- Homebrew installed on macOS (for installing `sqlcmd`).
- AdventureWorks2019 `.bak` file available on your local machine.

---

## **Setup SQL Server on Docker**

1. **Pull the SQL Server Docker image**:

   To download the latest SQL Server 2019 Docker image, run:
   ```bash
   docker pull mcr.microsoft.com/mssql/server:2019-latest
2. **Run the SQL Server container**:

   Use the following command to start the SQL Server container:
   ```bash
   docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourStrong@Passw0rd' -p 1434:1433 --name my_sql_container --platform linux/amd64 -d mcr.microsoft.com/mssql/server:2019-latest

- Replace `'YourStrong@Passw0rd'` with your custom password.
- `my_sql_container` is the name of the container.
- Port `1434` is mapped to your local machine and forwards to port `1433` inside the container.

### This command will:
- Pull and run the SQL Server 2019 container.
- Set the `SA_PASSWORD` to the provided password.
- Name the container `my_sql_container`.
- Expose port `1434` on the local machine and map it to port `1433` in the container.


### Install `sqlcmd` for macOS Using Homebrew

To install `sqlcmd`, follow these steps:

1. **Add the Microsoft SQL tap to Homebrew**:

   Run the following command to add Microsoft SQL to Homebrew:
   ```bash
   brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release

2. Install the mssql-tools package:

```bash
brew install mssql-tools
```
3. Add mssql-tools to your system's PATH for easier access by running the following 2 commands:
   ```bash
   echo 'export PATH="/usr/local/opt/mssql-tools/bin:$PATH"' >> ~/.profile
   source ~/.profile
   ```

### Create Backup Directory in the Container using the following command:
```bash
docker exec -it my_sql_container mkdir -p /var/opt/mssql/backup
```
### Copy .bak File to the Container:
```bash
docker cp "/path/to/your/AdventureWorks2019.bak" my_sql_container:/var/opt/mssql/backup/
```
- Replace `/path/to/your/AdventureWorks2019.bak` with the full path of your .bak file.

### Step-by-Step Guide to Install sqlcmd Inside the Container
1. Connect to the container interactively:
```bash
docker exec -u root -it my_sql_container bash
```
2. Install dependencies:
```bash
apt-get update
apt-get install curl apt-transport-https -y
apt-get install -y gnupg
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
```
3. Install mssql-tools and ODBC server:
```bash
ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```
4. Add sqlcmd to system path:
   ```bash
   echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
    source ~/.bashrc
   ```

### Restore Database from .bak File
1. Log in to the SQL Server container using sqlcmd:
```bash
docker exec -it my_sql_container /opt/mssql-tools/bin/sqlcmd -S localhost,1434 -U SA -P 'YourStrong@Passw0rd'

```
2. Run the following commands inside the sqlcmd interface to 
  - `Check the logical file names of the .bak file`:
```bash
RESTORE FILELISTONLY FROM DISK = '/var/opt/mssql/backup/AdventureWorks2019.bak';
GO
```
  - Restore the database using the logical names from the previous command output:
```bash
RESTORE DATABASE AdventureWorks2019 
FROM DISK = '/var/opt/mssql/backup/AdventureWorks2019.bak'
WITH MOVE 'AdventureWorks2019_Data' TO '/var/opt/mssql/data/AdventureWorks2019_Data.mdf', 
MOVE 'AdventureWorks2019_Log' TO '/var/opt/mssql/data/AdventureWorks2019_Log.ldf';
GO
```

3. Verify the Restoration

```sql
SELECT name FROM sys.databases;
GO
```
