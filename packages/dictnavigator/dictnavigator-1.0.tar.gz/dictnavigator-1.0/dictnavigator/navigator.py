
class DictNavigatorKey:
    """
    The DictNavigatorKey class provides functions for working with dictionaries of any nesting and depth.
    """

    def __init__(self, data):
        self.data = data

    def get_dict(self):
        """

        :return:
        - data: the dictionary with which the class will work.
        """
        return self.data

    def extract_keys_values(self, key, do_measure_depth=False):
        """
        Retrieves all keys and values from a dictionary at any depth that match a given key.

        If do_measure_depth is set to True,
        also includes information about the nesting depth in the form of a pair 'depth:depth value'

        :param key: key used for extraction.
        :param do_measure_depth: flag indicating whether nesting depth should be measured.
        :return result: List of dictionaries, where each dictionary contains a key and a value.
        """
        result = []
        self._extract_helper(self.data, key, result, do_measure_depth=do_measure_depth)
        return result

    def _extract_helper(self, data, key, result, do_measure_depth, depth=0):
        """
        The helper method for recursively extracting keys and values from a dictionary.

        :param data: dictionary or nested data structure.
        :param key: key used for extraction.
        :param result: list for saving results
        :param do_measure_depth: flag indicating whether nesting depth should be measured.
        :param depth: current nesting depth
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    if do_measure_depth:
                        result.append({k: v, "depth": depth})
                    else:
                        result.append({k: v})
                if isinstance(v, (dict, list, tuple)):
                    self._extract_helper(v, key, result, do_measure_depth, depth + 1)
        elif isinstance(data, (list, tuple)):
            for item in data:
                self._extract_helper(item, key, result, do_measure_depth, depth + 1)

    def update_value(self, key, old_value, new_value):
        """
        Updates key values at any dictionary depth.
        The old value is necessary in order to know exactly where to update it to a new one,
        because in nested structures the keys may be repeated.

        :param key: the key that needs to be updated.
        :param old_value: old key value.
        :param new_value: new key value.

        """
        self._update_helper(self.data, key, old_value, new_value)

    def _update_helper(self, data, key, old_value, new_value):
        """
        The helper method for recursively updating key values in a dictionary.

        :param data: dictionary or nested data structure.
        :param key: the key that needs to be updated.
        :param old_value: old key value.
        :param new_value: new key value.

        """

        if isinstance(data, dict):
            for k, v in data.items():
                if k == key and v == old_value:
                    data[k] = new_value
                if isinstance(v, (dict, list, tuple)):
                    self._update_helper(v, key, old_value, new_value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                self._update_helper(item, key, old_value, new_value)

    def delete_key(self, key, value):
        """
        Removes a key and value at any depth in the dictionary.
        The current value is necessary in order to know exactly where to delete,
        because in nested structures the keys may be repeated.

        :param key: the key that needs to be delete.
        :param value: the value that needs to be delete.

        """
        self._delete_helper(self.data, key, value)

    def _delete_helper(self, data, key, value):
        """
        The helper method for recursively removing a key and value from a dictionary.

        :param data: dictionary or nested data structure.
        :param key: the key that needs to be delete.
        :param value: the value that needs to be delete.

        """

        if isinstance(data, dict):
            for k, v in list(data.items()):
                if k == key and v == value:
                    del data[k]
                if isinstance(v, (dict, list, tuple)):
                    self._delete_helper(v, key, value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                self._delete_helper(item, key, value)

    def extract_all_keys(self):
        """
        Retrieves all keys from a dictionary at any depth.

        :return result: list all keys of dictionary.
        """
        result = []
        self._extract_all_keys_helper(self.data, result)
        return list(set(result))

    def _extract_all_keys_helper(self, data, result):
        """
        The helper method to recursively extract all keys from a dictionary.

        :param data: dictionary or nested data structure.
        :param result: list for saving results.

        """
        if isinstance(data, dict):
            for k, v in data.items():
                result.append(k)
                if isinstance(v, (dict, list, tuple)):
                    self._extract_all_keys_helper(v, result)
        elif isinstance(data, (list, tuple)):
            for item in data:
                self._extract_all_keys_helper(item, result)
