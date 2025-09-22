<p align="center">
<img src="https://pub-fbb2435be97c492d8ece0578844483ea.r2.dev/scailo-logo.png" alt="Scailo Logo" width="300"/>
</p>

<h1 align="center">Scailo Python SDK</h1>

<p align="center">
<strong>The official Python SDK for Scailo API.</strong>
</p>

<p align="center">
<a href="https://pypi.org/project/scailo-sdk/">
<img src="https://img.shields.io/pypi/v/scailo_sdk.svg" alt="PyPI version">
</a>
<a href="https://github.com/scailo/python-sdk/blob/main/LICENSE">
<img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
</a>
<a href="https://pypi.org/project/scailo-sdk/">
<img src="https://img.shields.io/pypi/pyversions/scailo_sdk.svg" alt="Python versions">
</a>
</p>

Welcome to the official Python SDK for Scailo, the next-generation ERP designed for modern businesses. This SDK provides a convenient way to interact with the Scailo API, enabling you to build powerful integrations, automate complex workflows, and create custom reports with ease.

Whether you're looking to handle workflow events, perform extensive customizations, or even generate detailed PowerPoint presentations from your ERP data, this SDK is your starting point.

## 🚀 Installation

You can install the Scailo SDK directly from PyPI:

```bash
pip install scailo_sdk
```

## ✨ Getting Started

Using the SDK is straightforward. First, you'll need to authenticate to get an auth_token, which you can then use to make subsequent API calls.

#### 1. Authentication

Here's how you can log in and retrieve your authentication token.

```python
import urllib3
from scailo_sdk.login import scailo_pb2 as login
from scailo_sdk.login_scailo_pb2_api import LoginServiceClient

# --- Your Scailo Credentials ---
# Replace with your Scailo instance domain and user credentials
SCAILO_DOMAIN = "[https://your-scailo-domain.com](https://your-scailo-domain.com)"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# 1. Create a login client
login_client = LoginServiceClient(SCAILO_DOMAIN, urllib3.PoolManager())

# 2. Call the login method to retrieve the auth token
try:
    login_req = login.UserLoginRequest(username=USERNAME, plain_text_password=PASSWORD)
    login_resp = login_client.login_as_employee_primary(login_req)
    
    auth_token = login_resp.auth_token
    print("Successfully authenticated!")
    # print(f"Auth Token: {auth_token}") # Be careful printing tokens

except Exception as e:
    print(f"Authentication failed: {e}")
    auth_token = None
```

#### 2. Making API Calls

Once you have the auth_token, you can use it in the extra_headers of your service client calls to access different parts of the Scailo API.

#### Example: Retrieve 10 Active Purchase Orders

This example shows how to fetch the 10 most recent active Purchase Orders.

```python
# Make sure you have the auth_token from the previous step
if auth_token:
    from scailo_sdk.purchases_orders import scailo_pb2 as purchases
    from scailo_sdk.purchases_orders_scailo_pb2_api import PurchasesOrdersServiceClient
    from scailo_sdk.base import scailo_pb2 as base

    # 1. Create the purchases client
    purchases_client = PurchasesOrdersServiceClient(SCAILO_DOMAIN, urllib3.PoolManager())

    # 2. Prepare the request
    filter_req = purchases.PurchasesOrdersServiceFilterReq(
        is_active=base.BOOL_FILTER_TRUE, 
        count=10
    )
    
    # 3. Retrieve active purchase orders using the auth_token
    try:
        resp = purchases_client.filter(
            filter_req, 
            extra_headers={"auth_token": auth_token}
        )
        print("Successfully retrieved Purchase Orders:")
        print(resp)
    except Exception as e:
        print(f"Failed to retrieve Purchase Orders: {e}")

```

#### Example: Retrieve 10 Active Goods Receipts

Similarly, you can query other services, like Goods Receipts.

```python
# Make sure you have the auth_token
if auth_token:
    from scailo_sdk.goods_receipts import scailo_pb2 as goodsreceipts
    from scailo_sdk.goods_receipts_scailo_pb2_api import GoodsReceiptsServiceClient
    from scailo_sdk.base import scailo_pb2 as base

    # 1. Create the Goods Receipts client
    goodsreceipts_client = GoodsReceiptsServiceClient(SCAILO_DOMAIN, urllib3.PoolManager())
    
    # 2. Prepare the request
    filter_req = goodsreceipts.GoodsReceiptsServiceFilterReq(
        is_active=base.BOOL_FILTER_TRUE, 
        count=10
    )

    # 3. Retrieve active Goods Receipts using the auth_token
    try:
        resp = goodsreceipts_client.filter(
            filter_req,
            extra_headers={"auth_token": auth_token}
        )
        print("Successfully retrieved Goods Receipts:")
        print(resp)
    except Exception as e:
        print(f"Failed to retrieve Goods Receipts: {e}")
```

## 📦 Repository

The source code for the Scailo Python SDK is hosted on GitHub.

GitHub Repository: https://github.com/scailo/python-sdk

Contributions, issues, and feature requests are welcome!

## 📄 License

This project is licensed under the Apache 2.0 License.