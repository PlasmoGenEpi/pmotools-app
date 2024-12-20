# pmotools-app

This repository contains the code for an app built with Streamlit that helps users convert their data into the PMO format using the [`pmotools-python`](https://github.com/PlasmoGenEpi/pmotools-python) package.

Contents 
- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Developer Notes](#developer-notes)

## Features

- Convert your data to PMO (in development)
    - Upload your data files (CSV, TXT, or XLSX)
    - Converts the data into PMO format using `pmotools`
    - Download the converted data as PMO

## Requirements

- Python 3.x
- Streamlit
- pmotools
- numpy 
- fuzzywuzzy

## Usage 

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/streamlit-pmo-converter.git
   cd streamlit-pmo-converter
2. Install the dependencies 
    ```bash
    pip install -r requirements.txt
3. Launch the app with 
    ```bash
    streamlit run PMO_Builder.py
## Developer Notes
