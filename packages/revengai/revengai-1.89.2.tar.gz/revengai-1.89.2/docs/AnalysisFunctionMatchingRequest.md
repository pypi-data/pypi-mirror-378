# AnalysisFunctionMatchingRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**min_similarity** | **float** | Minimum similarity expected for a match, default is 0.9 | [optional] [default to 0.9]
**filters** | [**FunctionMatchingFilters**](FunctionMatchingFilters.md) |  | [optional] 

## Example

```python
from revengai.models.analysis_function_matching_request import AnalysisFunctionMatchingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AnalysisFunctionMatchingRequest from a JSON string
analysis_function_matching_request_instance = AnalysisFunctionMatchingRequest.from_json(json)
# print the JSON string representation of the object
print(AnalysisFunctionMatchingRequest.to_json())

# convert the object into a dict
analysis_function_matching_request_dict = analysis_function_matching_request_instance.to_dict()
# create an instance of AnalysisFunctionMatchingRequest from a dict
analysis_function_matching_request_from_dict = AnalysisFunctionMatchingRequest.from_dict(analysis_function_matching_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


