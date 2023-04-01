"""Data types considered in OnTask and its relation with Pandas data types"""


class TypeDict(dict):
    """Class to detect multiple datetime types in Pandas."""

    def get(self, key):
        """Detect if given key is equal to any stored value."""
        return next(
            otype for dtype, otype in self.items() if key.startswith(dtype)
        )

datatype_names = TypeDict({
    'object': 'string',
    'int64': 'integer',
    'float64': 'double',
    'bool': 'boolean',
    'datetime64[ns': 'datetime',
})
