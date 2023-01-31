# EVE Account Creator

This repository is used to create EVE-online account in batches.


## How to use this repository

### 1. Build environment
```shell
pip install selenium==4.0.0 undetected-chromedriver==3.2.1
```

### 2. run

You need to provide these parameters. [Here is the example](example.py)

```python
from account_creator import Account_creator

# The recruit link, default is mine.
recruit_link = "https://www.eveonline.com/signup?invc=816999af-7d4c-4075-ab8f-e2310dd302bd"
# The email that will be bound to the account.
signup_email = "test@gmail.com"
# The base fields for signup-names. If None, It will use random 10 chars as base fields.
base_account = None
# If not None, The password will used for all newly created accounts.
signup_pwd = None
# How many account will be created
batch_num = 5

# create account
account_creator = Account_creator()
account_creator.account_creator(
    recruit_link=recruit_link,
    signup_email=signup_email,
    base_account=base_account,
    default_pwd=signup_pwd,
    batch_num=batch_num
)
```

---
#### Reference
* https://yescaptcha.atlassian.net/wiki/spaces/YESCAPTCHA/pages/28901377/Selenium