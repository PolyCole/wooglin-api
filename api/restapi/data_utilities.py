

# TODO Need to write test cases for this.
def apply_search_filters(data, query_params, is_staff=False):
    if 'phone' in query_params:
        data = data.filter(phone=query_params['phone'])

    if 'name' in query_params:
        data = data.filter(name=query_params['name'])

    if 'abroad_flag' in query_params:
        data = data.filter(abroad_flag=query_params['abroad_flag'])

    # For protected data.
    if is_staff:
        if 'member_score' in query_params:
            data = data.filter(member_score=query_params['member_score'])

    return data
