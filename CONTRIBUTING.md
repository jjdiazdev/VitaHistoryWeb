# Contributing to VitaHistory

Thank you for your interest in contributing to VitaHistory! This document provides guidelines for contributing to this project.

## License Notice

This project is licensed under the GNU General Public License v3.0 (GPLv3). By contributing to this project, you agree that your contributions will be licensed under the GPLv3 license.

## How to Contribute

1. Fork the repository and create your feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Reporting Issues

When reporting issues, please include as much detail as possible about your operating system, Python version, and steps to reproduce the issue.

## Development Setup

Follow these steps to set up the development environment locally.

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server** (running locally or remotely)
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/jjdiazdev/VitaHistoryWeb.git
cd VitaHistoryWeb
```

### 3. Create and Activate Virtual Environment

- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create MySQL Database
Ensure your MySQL server is running and create the database:
```sql
CREATE DATABASE vitahistory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Configure Environment Variables
VitaHistory requires the following environment variables (defined in `vitahistory/config.py`):

| Variable | Description | Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Secret key for Flask session security | `your_secret_key` |
| `MYSQL_HOST` | Database host address | `localhost` or `127.0.0.1` |
| `MYSQL_USER` | MySQL database user | `root` |
| `MYSQL_PASSWORD` | MySQL database password | `your_password` |
| `MYSQL_DATABASE` | Database name | `vitahistory` |


Set them in your current terminal session:

- **Windows (PowerShell):**
  ```powershell
  $env:SECRET_KEY="your_secret_key"
  $env:MYSQL_HOST="localhost"
  $env:MYSQL_USER="root"
  $env:MYSQL_PASSWORD="your_password"
  $env:MYSQL_DATABASE="vitahistory"
  ```
- **Windows (CMD):**
  ```cmd
  set SECRET_KEY=your_secret_key
  set MYSQL_HOST=localhost
  set MYSQL_USER=root
  set MYSQL_PASSWORD=your_password
  set MYSQL_DATABASE=vitahistory
  ```
- **Linux / macOS:**
  ```bash
  export SECRET_KEY="your_secret_key"
  export MYSQL_HOST="localhost"
  export MYSQL_USER="root"
  export MYSQL_PASSWORD="your_password"
  export MYSQL_DATABASE="vitahistory"
  ```

### 7. Run Database Migrations
Apply the migrations to set up the database schema:

- **PowerShell:**
  ```powershell
  $env:FLASK_APP="run.py"
  flask db upgrade
  ```
- **CMD:**
  ```cmd
  set FLASK_APP=run.py
  flask db upgrade
  ```
- **Linux / macOS:**
  ```bash
  export FLASK_APP=run.py
  flask db upgrade
  ```

### 8. Run the Application
Start the local development server:
```bash
python run.py
```
*(Or alternatively: `flask run`)*

Visit `http://127.0.0.1:5000/` in your browser.

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.
