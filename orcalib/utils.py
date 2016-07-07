#!/usr/bin/env python
# -*- coding: utf-8 -*-


def __check_filter_match(resource_val, filter):
    '''
    API to validate the resources against filters.
    It returns a list of indexes and the number of successful
    matches

    :type resource_val: type (str, int, dict, list)
    :param resource_val: Value of a matched key in the resource

    :type values: list
    :param values: a list of values to match against.
    '''

    values = filter['Values']

    # If the type is of 'str' or 'int'
    if type(resource_val) == str or \
       type(resource_val) == int:
        if resource_val in values:
            return True
    if type(resource_val) == list:
        for resval in resource_val:
            if type(resval) == str or \
                    type(resval) == int:
                if resval in values:
                    return True
            elif type(resval) == dict:
                print "Resource val is a dict: ", resval
                print "values are: ", values
                # For matching a list of dicts, the filter must have a
                # list of dicts as well.
                for value in values:
                    for resitem in resval.items():
                        for valitem in value.items():
                            if resitem[0] == valitem[0] and \
                                    resitem[1] == valitem[1]:
                                print "Matched: %s %s %s %s" % \
                                    (valitem[0], resitem[0],
                                     valitem[1], resitem[1])
                                return True
                            else:
                                print "Did not match %s %s %s %s" % \
                                    (valitem[0], resitem[0],
                                     valitem[1], resitem[1])

                    #for key in value.keys():
                    #    print "Key: ", key, value[key]

    return False

def __validate_input_filters(filters):
    # Validate input.
    if filters is None:
        print "No filters set"
        return False

    if type(filters) != list:
        print "Filters must be a list of key/value pairs"
        return False

    for filter in filters:
        if type(filter['Values']) != list:
            print "Filter Values must be a list of values"
            return False

    return True

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
    if not __validate_input_filters(filters):
        return None

    filtered_idxes = {}
    idx = 0
    for resource in resource_list:
        for filter in filters:
            name = filter['Name']
            resource_val = resource.get(name, None)

            if resource_val is None:
                    continue

            if __check_filter_match(resource_val, filter):
                if filtered_idxes.get(idx, None) is None:
                    filtered_idxes[idx] = 1
                else:
                    filtered_idxes[idx] += 1
        idx += 1

    filtered_list = []
    for idx in filtered_idxes.keys():
        if aggr_and:
            if filtered_idxes[idx] == len(filters):
                filtered_list.append(resource_list[idx])
        else:
            filtered_list.append(resource_list[idx])


    return filtered_list



