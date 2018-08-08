def format_skill_for_response(skill):
    formatted_skill = skill.to_mongo().to_dict()
    formatted_skill['id'] = str(formatted_skill['_id'])
    formatted_skill['created'] = formatted_skill['_id'].generation_time
    del formatted_skill['_id']

    for datetime_attr in ('created', 'last_update'):
        formatted_skill[datetime_attr] = formatted_skill[datetime_attr].timestamp()

    return formatted_skill
