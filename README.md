# freshservice-api-customobjects

Update Custom Object tables in Freshservice

## Overview

This is an example of reading from the Freshservice API, forming the results into a json object and posting that object to create some new records in a Freshservice Custom Object table.

The example checks for Agent Groups that have been created but do not exist in the Custom Object table yet, then creates those missing records.

## Setup

On a Linux system:

```sh
git clone <URL>
cd freshservice-api-scripts
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
cp sample.env .env
```

Edit the .env file to replace the placeholder values with your real values.

## Run

```sh
python3 main.py
```
