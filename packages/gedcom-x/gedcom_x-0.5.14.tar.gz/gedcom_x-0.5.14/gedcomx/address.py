from typing import Any, Dict, Optional, List

"""
======================================================================
 Project: Gedcom-X
 File:    address.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-09-03: _from_json_ refactoring
   - 2025-09-09: added schema_class
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .logging_hub import hub, logging
from .schemas import extensible
"""
======================================================================
Logging
======================================================================
"""
log = logging.getLogger("gedcomx")
serial_log = "gedcomx.serialization"
#=====================================================================

@extensible()
class Address:
    """A GedcomX Address Data Type
    A GedcomX Address Data Type.

    Represents a postal address according to the GedcomX conceptual model.

    Args:
        value (str, optional): A complete address as a single string.
        city (str, optional): Name of the city or town.
        country (str, optional): Name of the country.
        postalCode (str, optional): Postal or ZIP code.
        stateOrProvince (str, optional): Name of the state, province, or region.
        street (str, optional): First street address line.
        street2 (str, optional): Second street address line.
        street3 (str, optional): Third street address line.
        street4 (str, optional): Fourth street address line.
        street5 (str, optional): Fifth street address line.
        street6 (str, optional): Sixth street address line.
    """

    identifier = "http://gedcomx.org/v1/Address"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[str] = None,
                 city: Optional[str] = None,
                 country: Optional[str] = None,
                 postalCode: Optional[str] = None,
                 stateOrProvince: Optional[str] = None,
                 street: Optional[str] = None,
                 street2: Optional[str] = None,
                 street3: Optional[str] = None,
                 street4: Optional[str] = None,
                 street5: Optional[str] = None,
                 street6: Optional[str] = None):
        
        self._value = value #TODO impliment a parser for date strings.
        self.city = city
        self.country = country
        self.postalCode = postalCode
        self.stateOrProvince = stateOrProvince
        self.street = street
        self.street2 = street2
        self.street3 = street3
        self.street4 = street4
        self.street5 = street5
        self.street6 = street6

    @property
    def value(self) -> str: 
        return ', '.join(filter(None, [
            self.street, self.street2, self.street3,
            self.street4, self.street5, self.street6,
            self.city, self.stateOrProvince,
            self.postalCode, self.country
        ]))
    
    @value.setter
    def value(self,value: str):
        self._value = value
        return
        raise NotImplementedError("Parsing of a full address is not implimented.")
    
    def _append(self,value):
        if self._value:
            self._value = self._value + ' ' + value
        else:
            self._value = value
             
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return (
            self.value == other.value and
            self.city == other.city and
            self.country == other.country and
            self.postalCode == other.postalCode and
            self.stateOrProvince == other.stateOrProvince and
            self.street == other.street and
            self.street2 == other.street2 and
            self.street3 == other.street3 and
            self.street4 == other.street4 and
            self.street5 == other.street5 and
            self.street6 == other.street6
        )
    
    def __str__(self) -> str:
        # Combine non-empty address components into a formatted string
        parts = [
            self._value,
            self.street,
            self.street2,
            self.street3,
            self.street4,
            self.street5,
            self.street6,
            self.city,
            self.stateOrProvince,
            self.postalCode,
            self.country
        ]

        # Filter out any parts that are None or empty strings
        filtered_parts = [str(part) for part in parts if part]

        # Join the remaining parts with a comma and space
        return ', '.join(filtered_parts)
    
    @property
    def _as_dict_(self):
        with hub.use(serial_log):
            log.debug(f"Serializing 'Address' with value: '{self.value}'")
            type_as_dict = {}
            if self.city: type_as_dict["city"] = self.city
            if self.country: type_as_dict["country"] = self.country
            if self.postalCode: type_as_dict["postalCode"] = self.postalCode
            if self.stateOrProvince: type_as_dict["stateOrProvince"] = self.stateOrProvince
            if self.street: type_as_dict["street"] = self.street
            if self.street2: type_as_dict["street2"] = self.street2
            if self.street3: type_as_dict["street3"] = self.street3
            if self.street4: type_as_dict["street4"] = self.street4
            if self.street5: type_as_dict["street5"] = self.street5
            if self.street6: type_as_dict["street6"] = self.street6
            log.debug(f"'Address' serialized with fields: '{type_as_dict.keys()}'") 
            if type_as_dict == {} or len(type_as_dict.keys()) == 0: log.warning("serializing and empty 'Address' Object")

        return type_as_dict if type_as_dict != {} else None
        
    
    @classmethod
    def _from_json_(cls, data: Any, context: Any = None) -> "Address":
        """
        Build an Address from JSON.
        Supports:
          - Shorthand string -> value
          - Aliases: postal_code/postal -> postalCode; state/province -> stateOrProvince
          - Line aliases: line1..line6 / address1..address6 / addr1..addr6 -> street..street6
          - 'lines': [..] list -> street..street6
        """
        if data is None: return None
        
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}._from_json_ expected dict or str, got {type(data)}")

        address_data: Dict[str, Any] = {}

        # Freeform value (accept a few aliases)
        if (v := data.get("value")) is None:
            address_data["value"] = str(v)

        # Simple scalars
        if (city := data.get("city")) is not None:
            address_data["city"] = city
        if (country := data.get("country")) is not None:
            address_data["country"] = country

        # Postal code (aliases)
        if (postal := data.get("postalCode")) is not None:
            address_data["postalCode"] = postal

        # State / Province (aliases)
        if (stateprov := data.get("stateOrProvince")) is not None:
            address_data["stateOrProvince"] = stateprov

        if data.get("street") is not None:
            address_data["street"] = data["street"]

        if data.get("street2") is not None:
            address_data["street2"] = data["street2"]

        if data.get("street3") is not None:
            address_data["street3"] = data["street3"]

        if data.get("street4") is not None:
            address_data["street4"] = data["street4"]

        if data.get("street5") is not None:
            address_data["street5"] = data["street5"]

        if data.get("street6") is not None:
            address_data["street6"] = data["street6"]


        return cls(**address_data)


