import yaml
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_openapi_yaml(path: Path) -> Dict:
    """Загружает OpenAPI спецификацию из YAML-файла в словарь."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_ref(ref: str, openapi_dict: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"Поддерживаются только локальные $ref: {ref}")
    parts = ref[2:].split("/")  # отрезаем "#/" и разбиваем
    current = openapi_dict
    for part in parts:
        current = current[part]
    return current


contract = load_openapi_yaml('apps/profiles/contracts/user_profile_view.yml')

print(contract.keys())
print(contract['paths'].keys())
print(list(contract['paths'].keys())[0])
print(contract['paths']['/profiles/{id}/'].keys())
print(f"{contract['paths']['/profiles/{id}/']['post'].keys()=}")
print(f"{contract['paths']['/profiles/{id}/']['post']['requestBody']['content']['application/json']['examples']['BaseRequestBodyFields']['value']=}")
# print(contract['paths']['/profiles/{id}/']['get']['operationId'])
# print(contract['paths']['/profiles/{id}/']['get']['description'])
# print(contract['paths']['/profiles/{id}/']['get']['summary'])
print(f"{contract['paths']['/profiles/{id}/']['get']['parameters']=}")
operation = contract['paths']['/profiles/{id}/']['get']
parameters_in_path = list(filter(lambda param: param['in'] == 'path', operation['parameters']))
print(f"{parameters_in_path=}")
param_names = list(filter(lambda param: param['name'] == 'id', parameters_in_path))
print(f"{param_names=}")
cleaned_params = {
    param['name']: 1 for param in param_names
}
print(f"{cleaned_params=}")
[print(f"{contract['paths']['/profiles/{id}/']['get']['parameters'][i]=}") for i in range(len(contract['paths']['/profiles/{id}/']['get']['parameters']))]
# print(contract['paths']['/profiles/{id}/']['get']['security'])
print(contract['paths']['/profiles/{id}/']['get']['responses'])
print(contract['paths']['/profiles/{id}/']['get']['responses']['200'])
print(contract['paths']['/profiles/{id}/']['get']['responses']['200']['content'])

ref = resolve_ref(contract['paths']['/profiles/{id}/']['get']['responses']['200']['content']['application/json']['schema']['$ref'], contract)
cleaned_ref = dict(
    filter(
        lambda property: 'allOf' not in property[1].keys(), filter(
        lambda property: 'oneOf' not in property[1].keys(), ref['properties'].items()
    ))
)
print(f"{ref.keys()=}")
print(f"{ref['type']=}")
print(f"{ref['description']=}")
print(f"{ref['properties']=}")
print(f"{cleaned_ref=}")
print(f"{ref['properties'].keys()=}")
print(f"{ref['properties']['first_name']=}")
print(f"{ref['properties']['first_name']['type']=}")
print(f"{ref['properties']['first_name']['maxLength']=}")
print(f"{ref['required']=}")

