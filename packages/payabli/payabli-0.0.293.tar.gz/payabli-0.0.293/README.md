# Payabli Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Fpayabli%2Fsdk-python)
[![pypi](https://img.shields.io/pypi/v/payabli)](https://pypi.python.org/pypi/payabli)

The Payabli Python library provides convenient access to the Payabli APIs from Python.

## Documentation

API reference documentation is available [here](https://docs.payabli.com).

## Installation

```sh
pip install payabli
```

## Reference

A full reference for this library is available [here](https://github.com/payabli/sdk-python/blob/HEAD/./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from payabli import PaymentDetail, PayMethodCredit, PayorDataRequest, payabli

client = payabli(
    api_key="YOUR_API_KEY",
)
client.money_in.getpaid(
    customer_data=PayorDataRequest(
        customer_id=4440,
    ),
    entry_point="f743aed24a",
    ipaddress="255.255.255.255",
    payment_details=PaymentDetail(
        service_fee=0.0,
        total_amount=100.0,
    ),
    payment_method=PayMethodCredit(
        cardcvv="999",
        cardexp="02/27",
        card_holder="Kassiane Cassian",
        cardnumber="4111111111111111",
        cardzip="12345",
        initiator="payor",
    ),
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
import asyncio

from payabli import (
    Asyncpayabli,
    PaymentDetail,
    PayMethodCredit,
    PayorDataRequest,
)

client = Asyncpayabli(
    api_key="YOUR_API_KEY",
)


async def main() -> None:
    await client.money_in.getpaid(
        customer_data=PayorDataRequest(
            customer_id=4440,
        ),
        entry_point="f743aed24a",
        ipaddress="255.255.255.255",
        payment_details=PaymentDetail(
            service_fee=0.0,
            total_amount=100.0,
        ),
        payment_method=PayMethodCredit(
            cardcvv="999",
            cardexp="02/27",
            card_holder="Kassiane Cassian",
            cardnumber="4111111111111111",
            cardzip="12345",
            initiator="payor",
        ),
    )


asyncio.run(main())
```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from payabli.core.api_error import ApiError

try:
    client.money_in.getpaid(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from payabli import payabli

client = payabli(
    ...,
)
response = client.money_in.with_raw_response.getpaid(...)
print(response.headers)  # access the response headers
print(response.data)  # access the underlying object
```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

A request is deemed retryable when any of the following HTTP status codes is returned:

- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Errors)

Use the `max_retries` request option to configure this behavior.

```python
client.money_in.getpaid(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python

from payabli import payabli

client = payabli(
    ...,
    timeout=20.0,
)


# Override timeout for a specific method
client.money_in.getpaid(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from payabli import payabli

client = payabli(
    ...,
    httpx_client=httpx.Client(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
