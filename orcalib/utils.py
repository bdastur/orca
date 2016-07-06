#!/usr/bin/env python
# -*- coding: utf-8 -*-



def filter_list(resource_list, filters, aggr_and=False):
    '''
    Return a filtered list of resources.
    This is a generic API to filter any list.
    :type resource_list: List of dictionaries.
    :param resource_list: List of resources.

    :type filters: List of dictionaries (key/value pairs)
    :param filters: List of filters to apply to the resource list

    Defining filters:
    =================
    It is a list of key, value pairs that can be passed to
    match against the records in resource list.
    filters = [{'Name': <key>, 'Values':['<value>',..]}]
    ---------------------------

    :type aggr_and: Boolean
    :param aggr_and: A flag to indicate whether to apply an
        and or or operation to aggregate result. This is applicable
        when you have more than one key/value pairs in the filters.
        Default behavior is an OR. meaning if either of the key/value pair
        mathces it is added to the filtered list.

    Returns:
        None: If any validation fails.
        filtered_list: A list of filtered resource upon success.
    '''
    # Validate input.
    if filters is None:
        print "No filters set"
        return None

    if type(filters) != list:
        print "Filters must be a list of key/value pairs"
        return None

    for filter in filters:
        if type(filter['Values']) != list:
            print "Filter Values must be a list of values"
            return None

    filtered_idxes = {}
    idx = 0
    for resource in resource_list:
        for filter in filters:
            name = filter['Name']
            values = filter['Values']

            resource_val = resource.get(name, None)

            if resource_val is None:
                    continue

            # If the type is of 'str' or 'int'
            if type(resource_val) == str or \
                    type(resource_val) == int:
                if resource_val in values:
                    if filtered_idxes.get(idx, None) is None:
                        filtered_idxes[idx] = 1
                    else:
                        filtered_idxes[idx] += 1
            if type(resource_val) == list:
                for resval in resource_val:
                    if resval in values:
                        if filtered_idxes.get(idx, None) is None:
                            filtered_idxes[idx] = 1
                        else:
                            filtered_idxes[idx] += 1
                        break
        idx += 1

    filtered_list = []
    for idx in filtered_idxes.keys():
        if aggr_and:
            if filtered_idxes[idx] == len(filters):
                print "Add to list since and"
                filtered_list.append(resource_list[idx])
        else:
            filtered_list.append(resource_list[idx])


    return filtered_list



