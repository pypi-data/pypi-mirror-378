# FunctionMatchingResultWithBestMatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**function_id** | **int** |  | 
**matched_function** | [**MatchedFunction**](MatchedFunction.md) |  | 
**suggested_name** | **str** |  | [optional] 
**suggested_name_confidence** | **float** |  | [optional] 

## Example

```python
from revengai.models.function_matching_result_with_best_match import FunctionMatchingResultWithBestMatch

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionMatchingResultWithBestMatch from a JSON string
function_matching_result_with_best_match_instance = FunctionMatchingResultWithBestMatch.from_json(json)
# print the JSON string representation of the object
print(FunctionMatchingResultWithBestMatch.to_json())

# convert the object into a dict
function_matching_result_with_best_match_dict = function_matching_result_with_best_match_instance.to_dict()
# create an instance of FunctionMatchingResultWithBestMatch from a dict
function_matching_result_with_best_match_from_dict = FunctionMatchingResultWithBestMatch.from_dict(function_matching_result_with_best_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


