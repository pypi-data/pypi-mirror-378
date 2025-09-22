"""
Table name constants for Dataverse tables.

This module provides an Enum with all available table logical names
for convenient usage with DataverseTable.
"""

from enum import Enum


class Tables(Enum):
    """Enum containing all available Dataverse table logical names"""

    # === INVENTORY AND PRODUCTION ===
    ARTICLE = "iony_article"
    RECIPE = "iony_recipe"
    INGREDIENT = "iony_ingredient"
    PROCESS = "iony_process"
    BATCH = "iony_batch"
    FABRICATION = "iony_fabrication"
    CONSUMPTION = "iony_consumption"
    PROPERTY = "iony_property"

    # === TESTING ===
    R2RSESSIONS = "iony_r2rsession"

    def __str__(self):
        """Return the table logical name when converted to string"""
        return self.value

    @classmethod
    def list_all(cls):
        """Return a list of all table logical names"""
        return [table.value for table in cls]

    @classmethod
    def display_names(cls):
        """Return a dictionary mapping enum names to logical names"""
        return {table.name: table.value for table in cls}
