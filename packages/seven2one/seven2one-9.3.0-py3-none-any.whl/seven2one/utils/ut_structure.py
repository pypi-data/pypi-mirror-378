from collections import namedtuple
from typing import Any

class Structure():
    queryStructure = f'''query inventories {{
    inventories (pageSize:1000) {{
        name
        inventoryId
        displayValue
        isDomainUserType
        hasValidityPeriods
        historyEnabled
        propertyUniqueness {{
            uniqueKey
            properties
            }}
        variant {{
            name
            properties {{
                name
                type
                isArray
                nullable
                }}
            }}
        properties {{
            name
            ...Scalar
            type
            isArray
            nullable
            propertyId
            ... Reference 
            }}
        }}
    }}
    fragment Scalar on IScalarProperty {{
        dataType
        }}
    fragment Reference on IReferenceProperty {{
        inventoryId
        inventoryName
        }}
    '''

    @staticmethod
    def introspection_query_string():
        introspectionQueryString = r'''
            query IntrospectionQuery { __schema { queryType { name } mutationType 
                { name } subscriptionType { name } types { ...FullType } directives
                { name description locations args { ...InputValue } } } }

            fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args 
                { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces 
                { ...TypeRef } enumValues(includeDeprecated: true) { name  } possibleTypes { ...TypeRef } } 

            fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } 
            fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType 
                    { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }
        '''
        return introspectionQueryString
    
    @staticmethod
    def full_structure_dict(structure) -> dict:
        """Converts the query of all inventories with all fields into a pure dict"""

        def subdict(inputObject, name):
            itemDict = {}
            for item in inputObject:
                itemDict.setdefault(item[name], {})
                for k, v in item.items():
                    itemDict[item[name]].setdefault(k, v)
            return itemDict

        structureDict = {}
        for inventory in structure['inventories']:
            inventoryName = inventory['name']
            structureDict.setdefault(inventoryName, {})
            for definitionKey, definitionValue in inventory.items():
                if not isinstance(definitionValue, (list, dict)):
                    structureDict[inventoryName].setdefault(
                        definitionKey, definitionValue)
                else:
                    if definitionKey == 'properties':
                        subDict = subdict(inventory[definitionKey], 'name')
                        structureDict[inventoryName].setdefault(
                            definitionKey, subDict)
                    if definitionKey == 'propertyUniqueness':
                        subDict = subdict(
                            inventory[definitionKey], 'uniqueKey')
                        structureDict[inventoryName].setdefault(
                            definitionKey, subDict)
                    if definitionKey == 'variant':
                        structureDict[inventoryName].setdefault(
                            definitionKey, {})
                        structureDict[inventoryName][definitionKey].setdefault(
                            'name', definitionValue['name'] if isinstance(definitionValue, dict) else '')
                        subDict = subdict(
                            inventory[definitionKey]['properties'], 'name')
                        structureDict[inventoryName][definitionKey].setdefault(
                            'properties', subDict)
        return structureDict

    @staticmethod
    def full_Structure_NT(structure: dict) -> Any:
        """
        Provides the complete data structure of dynamic objects as named tuple. 
        Needs structureDict first
        """
        def _subItem(object: dict):
            Item = namedtuple('Item', object.keys())
            itemDict = {}
            for key, value in object.items():
                if isinstance(value, dict):
                    subItem = _subItem(value)
                    itemDict.setdefault(key, subItem)
                else:
                    itemDict.setdefault(key, value)
            item = Item(**itemDict)
            return item

        Item = namedtuple('Item', structure.keys())
        itemDict = {}
        for key, value in structure.items():
            if isinstance(value, dict):
                subItem = _subItem(value)
                itemDict.setdefault(key, subItem)
            else:
                itemDict.setdefault(key, value)
        return Item(**itemDict)

    @staticmethod
    def inventory_NT(structure) -> Any:
        """
        Provides a simplified namedtuple of dynamic objects for interactive usage
        """
        inventoryDict = {key: key for key in structure.keys()}
        Inventories = namedtuple('Inventories', inventoryDict.keys())
        return Inventories(**inventoryDict)

    @staticmethod
    def inventory_Property_NT(structure) -> Any:
        """
        Provides a simplified namedtuple of inventory properties for interactive usage
        """
        Inventory = namedtuple('Inventories', structure.keys())
        inventoryDict = {}

        for inventory in structure.keys():
            propertyDict = {}
            Properties = namedtuple('Properties', propertyDict.keys())
            properties = Properties(**propertyDict)
            for key in structure[inventory]['properties'].keys():
                propertyDict.setdefault(key, key)
                Properties = namedtuple('Properties', propertyDict.keys())
                properties = Properties(**propertyDict)
            inventoryDict.setdefault(inventory, properties)
        return Inventory(**inventoryDict)

