protected_fields = ['member_score', 'address', 'present', 'temp_password']


# TODO Need to write test cases for this.
# TODO: There's definitely room for optimization here. Need to implement the industry standard filtering method.
#  Need to move on now though.
def apply_search_filters(data, query_params, is_staff=False):
    if 'phone' in query_params:
        data = data.filter(phone=query_params['phone'])

    if 'name' in query_params:
        name = de_urlify(query_params['name'], len(query_params['name']))
        data = data.filter(name=name)

    if 'abroad_flag' in query_params:
        data = data.filter(abroad_flag=query_params['abroad_flag'])

    # For protected data.
    if is_staff:
        if 'member_score' in query_params:
            data = data.filter(member_score=query_params['member_score'])

    return data


# TODO Need to write test cases for this.
# TODO Implement best practices here.
def apply_ordering(data, query_params, is_staff=False):
    order_operations = query_params['order_by'].split(",")

    for order_request in order_operations:
        processed = order_request.split(".")

        operation = processed[0]

        if processed[1] == "desc":
            operation = "-" + operation

        if processed[0] in protected_fields:
            if is_staff:
                data = data.order_by(operation)
            else:
                return "You've attempted to sort by a field you do not have permission to view."
        else:
            data = data.order_by(operation)

    return data


# Takes a string and returns the string in normal format.
def de_urlify(in_string, in_string_length):
    return in_string[:in_string_length].replace('%20', ' ')
