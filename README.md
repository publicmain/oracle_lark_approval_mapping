# Lark to NetSuite Vendor Bill Automation

## Overview

This project automates the integration between **Lark (Feishu)** and **NetSuite Vendor Bills** for **Shanghai DALAI Company**. It streamlines the approval process by automatically transferring approval reports from Lark to NetSuite, eliminating manual data entry, reducing errors, and enhancing operational efficiency.

## Features

- **Automated Data Transfer:** Seamlessly fetches and processes three types of approval reports: Non-PO Bill Invoices, Purchase Orders, and PO-linked Bill Invoices.
- **Secure API Integration:** Utilizes **OAuth1** authentication to securely interact with NetSuite’s RESTlet API.
- **Data Mapping & Transformation:** Accurately maps complex approval fields to NetSuite’s internal identifiers, ensuring data integrity.
- **Concurrency Management:** Implements multithreading with **threading Locks** to prevent duplicate processing and ensure thread-safe operations.
- **Attachment Handling:** Downloads, encodes in **Base64**, and attaches various file types from Lark to NetSuite records with appropriate MIME types.
- **Comprehensive Logging:** Uses Python’s **logging** library with **RotatingFileHandler** to log successes and errors for efficient monitoring and troubleshooting.
- **Error Handling:** Robust mechanisms to capture and manage exceptions, maintaining system reliability.

## Technologies Used

- **Programming Language:** Python
- **Framework:** Flask
- **APIs:** Lark Approval API, NetSuite RESTlet API
- **Authentication:** OAuth1
- **Libraries:** Requests, Logging, Threading, Base64, JSON
- **Deployment:** Can be deployed on any server supporting Python and Flask

## Installation

### Prerequisites

- Python 3.8+
- Flask
- Required Python libraries (listed in `requirements.txt`)

### Steps

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/lark-netsuite-automation.git
    cd lark-netsuite-automation
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Environment**
    - Create a `config.py` file with necessary configurations such as API credentials.
    - Ensure the `logs` directory exists:
      ```bash
      mkdir logs
      ```

4. **Run the Application**
    ```bash
    python app.py
    ```
    The Flask server will start on `0.0.0.0:10083`.

## Usage

The application exposes the following API endpoints:

- **GET /**: Check if the API is running.
- **GET /api/bill**: Process bill approval instances and create Vendor Bills in NetSuite.
- **GET /api/po**: Process purchase order approval instances and create Purchase Orders in NetSuite.
- **GET /api/polinked**: Process PO-linked bill approval instances and create linked Vendor Bills in NetSuite.

### Example Request

To process bill approvals, send a GET request to:

http://<server_ip>:10083/api/bill


## Logging

Logs are stored in the `logs` directory with separate files for each process type (e.g., `bill_success.log`, `bill_error.log`). Logs include timestamps, log levels, and detailed messages for both successful operations and errors.

## Challenges

The main challenges included ensuring data integrity during complex system integrations and managing high concurrency to prevent duplicate processing, all while maintaining secure API connections and robust file handling.

## Project Outcome

- **Efficiency Improvement:** Automated the approval process, reducing manual workload by several hours monthly.
- **Accuracy Enhancement:** Minimized data entry errors through reliable automated mappings and validations.
- **Operational Reliability:** Achieved seamless, scalable integration with comprehensive logging and error handling.

## Contact

For any questions or support, please contact [Yao Kexiang](e0893440@u.nus.edu).

---
