# FunctionMatchingBatchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_id** | **int** |  | [optional] 
**scope** | [**FunctionMatchingScopeRequest**](FunctionMatchingScopeRequest.md) | Scope of the function matching request, used to limit the search to specific binaries, collections, and functions | 

## Example

```python
from revengai.models.function_matching_batch_request import FunctionMatchingBatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionMatchingBatchRequest from a JSON string
function_matching_batch_request_instance = FunctionMatchingBatchRequest.from_json(json)
# print the JSON string representation of the object
print(FunctionMatchingBatchRequest.to_json())

# convert the object into a dict
function_matching_batch_request_dict = function_matching_batch_request_instance.to_dict()
# create an instance of FunctionMatchingBatchRequest from a dict
function_matching_batch_request_from_dict = FunctionMatchingBatchRequest.from_dict(function_matching_batch_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


