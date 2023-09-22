# freshservice-api-scripts

Read and update content in Freshservice tenants via their REST API

## Overview

This is has examples of reading from the Freshservice API, forming the results into a json object and making changes back in the tenant.

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
