# Local UI Guide

This document explains how to run the enhanced login and dashboard UI locally without Docker.

## Requirements

- Python 3.x installed on your machine

## Quick Start (Recommended Method)

To run the complete solution, you'll need to run two services in separate terminal windows:

### Terminal 1: Start the API Server

```bash
cd /Users/mikail/Desktop/BDC
./run_api_only.sh
```

### Terminal 2: Start the HTML Server

```bash
cd /Users/mikail/Desktop/BDC
./run_html_only.sh
```

### Access the UI

Once both servers are running, open your browser and go to:
http://localhost:8090/

From this landing page, you can access both the enhanced login and dashboard pages.

## Alternative Methods

The project includes several other ways to start the services:

### Using the Combined Script

```bash
cd /Users/mikail/Desktop/BDC
./run_simple_ui.sh
```

This script will start both the API and HTML servers, and automatically open the login page in your browser.

### Manual Start

If you prefer to run the components manually:

1. Start the modified API server:
```bash
cd /Users/mikail/Desktop/BDC
sed 's/port=8888/port=9888/' server/complete_test_api.py | python3
```

2. Start an HTTP server for the client files in a new terminal:
```bash
cd /Users/mikail/Desktop/BDC/client
python3 -m http.server 8090
```

## Test Accounts

You can use the following test accounts to log in:

| Role       | Email             | Password    |
|------------|-------------------|-------------|
| Admin      | admin@bdc.com     | Admin123!   |
| Tenant     | tenant@bdc.com    | Tenant123!  |
| Trainer    | trainer@bdc.com   | Trainer123! |
| Student    | student@bdc.com   | Student123! |

## Troubleshooting

If you encounter any issues:

1. Check that ports 8090 and 9888 are not already in use on your system
2. Ensure both the API and HTML servers are running
3. Try accessing the API directly at http://localhost:9888/health to verify it's working
4. If the login doesn't work, make sure JavaScript is enabled in your browser
5. Check the browser console for any error messages