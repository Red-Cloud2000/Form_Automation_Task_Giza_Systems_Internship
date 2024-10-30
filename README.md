# Form Automation Task - Giza Systems Internship

## 📄 Overview
This repository contains the automation scripts developed as part of the Form Automation Task assigned during the Giza Systems Internship. The task involves using Selenium WebDriver to automate form interactions, covering both positive and negative scenarios for input validation.

## Table of Contents
- [📄 Overview](#-overview)
- [✨ Features](#-features)
- [🔧 Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
## Project Overview

The Form Automation Task focuses on automating a form's end-to-end testing, ensuring comprehensive validation for multiple scenarios. This project applies skills from the Giza Systems training program, with emphasis on creating robust test cases and logging mechanisms.

## ✨ Features

- **Automated form submission**: Automates filling and submitting forms with various input scenarios.
- **Validation tests**: Includes both positive and negative test cases.
- **Error logging**: Logs errors to a CSV file with details on the error message, suite name, test case title, and input data.

## 🔧 Installation

### Prerequisites
Ensure the following are installed before running the project:
- **Python** 3.12.4
- **Selenium** package
- **WebDriver** (e.g., ChromeDriver for Google Chrome)
- **Pytest Package**
  ```bash
   pip install pytest
   ```

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/Red-Cloud2000/Form_Automation_Task_Giza_Systems_Internship.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Form_Automation_Task_Giza_Systems_Internship
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
- **Run tests**:
   ```bash
   pytest .\Registration_Form_Testing.py
   ```
3. **Review logs**: After running, check the `error_log.csv` for any issues encountered during testing.

## Contributing

Please open an issue if you encounter a bug or have suggestions for improvement. Contributions are welcome!
