"""
Context proccessors for html templates.
"""


def user_type_processor(request):
    if request.user.is_authenticated:
        return {'user_type': request.user.user_type,
                'user': request.user}
    return {'user_type': None}
