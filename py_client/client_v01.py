import requests

# endpoint="https://httpbin.org/status/200"
endpoint="http://127.0.0.1:8000/api/"

# get_response = requests.get(endpoint)
get_response = requests.get(endpoint, params={"abc": 123, "xyz":456}, json={"query": "Hello World"})
# print(get_response)
# print(get_response.status_code)
# print(get_response.connection)
# print(get_response.cookies)
# print(get_response.elapsed)
print(get_response.json())
print(get_response.status_code)