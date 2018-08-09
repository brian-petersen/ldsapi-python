# ldsorg

This project is a fork of [LDS-org](https://github.com/jidn/LDS-org). The motiviation for this project is the same: I am a ward clerk and needed a way to pull data from lds.org in an easy manner.

## Install

The easiest way for now is to clone the repo and install it manually:

```sh
git clone git@github.com:brian-petersen/ldsorg-python.git
cd ldsorg-python
python setup.py install
```

## Quick Start

The `ldsorg` module provides two nicities, a `Client` class and a `session` function. The following examples demonstrate their basic usage.

```python
from ldsorg import Client

lds_client = Client
lds_client.sign_in('user', 'pass')

res = lds_client.get('current-user-id')

print(res.json())

lds_client.get('signout-url')
```

```python
from ldsorg import session

with session('user', 'pass') as lds_client:
    res = lds_client.get('current-user-id')
    ...
```

## Endpoints

The `Client` class retrieves URLs based on endpoints. Most endpoint URLs reply with JSON resources. The list of available endpoints is dynamically generated as discussed at https://tech.lds.org/wiki/LDS_Tools_Web_Services. The list of endpoints is found at https://tech.lds.org/mobile/ldstools/config.json.

Some endpoint URLs accept parameters. These are loosely documented at https://tech.lds.org/wiki/LDS_Tools_Web_Services.

The `Client` class retreives the latest endpoints list when instantiated. It replaces the parameter values when appropiate. Any `unit` parameters are auto-filled with the authorized users unit number.

The following example shows how to get a list of available endpoints and their parameters:

```python
import pprint from pprint
from ldsorg import session

with session('user', 'pass') as client:
    pprint(client._endpoints)
```

### Photos Example

The `photo-url` endpoint needs two arguments, an member ID and the type of photo.  The photo type is either 'household' or 'individual'.  See [LDS Tools Web Services](https://tech.lds.org/wiki/LDS_Tools_Web_Services#Signin_services) for more information.

```python
from pprint import pprint
from ldsorg import session

with session('user', 'pass') as client:
    my_id = lds.get('current-user-id').json()
    res = lds.get('photo-url', 'individual', member=my_id)

    pprint(res.json())
```

## Todo

- [ ] Ensure original test cases work

## Original License

Copyright (c) 2017 Clinton James

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
