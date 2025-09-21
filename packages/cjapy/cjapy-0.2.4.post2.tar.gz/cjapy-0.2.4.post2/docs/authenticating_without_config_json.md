[Back to README](../README.md)

# How to authenticate without using a config.json file

This is necessary when you run scripts with the cjapy library on certain server environments (e.g. Google Cloud) instead of locally (e.g. in a Jupyter Notebook.\
In such environments, referring to config.json may not work.\
In that case, you can pass the variables to the configure method available.

## 1. Create your different environment variables

In windows command line:

```shell
setx NEWVAR SOMETHING
```

In Powershell:

```shell
$Env:<variable-name> = "<new-value>"
```

Linux / Unix / iOS shells:

```shell
export NAME=VALUE
```

## 2. Accessing the variable in your python script

You can then access the different values in your python script by realizing the following command:

```python
import os

USER = os.getenv('API_USER')
PASSWORD = os.environ.get('API_PASSWORD')
...
```

## 3. using the configure method

The `cjapy` module provide a configure method that will set the correct value to be used in the module.

```python
import os

my_org_id = os.getenv('org_id')
my_tech_id = os.environ.get('tech_id')
my_secret = os.environ.get('secret')
my_client_id = os.environ.get('client_id')
my_scopes = os.environ.get('scopes')

import cjapy

cjapy.configure(org_id=my_org_id,tech_id=my_tech_id, secret=my_secret,client_id=my_client_id,scopes=my_scopes)

```

Starting this point, you can use the `cjapy` module as explained in the documentation.
