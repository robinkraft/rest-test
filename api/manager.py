from flask import Flask
from flask.json import jsonify
from flask import make_response


app = Flask(__name__)

EXPECTED_KEYS = ['first_name', 'last_name', 'userid', 'groups']

USERS = dict(jsmith=dict(first_name='Joe',
                         last_name='Smith',
                         userid='jsmith',
                         groups=['admins', 'users']))

GROUPS = dict(admins=['jsmith'], users=['jsmith'])


def make_error_response(error_code, msg):
    """Form proper Flask reponse object for use with errors."""
    return make_response(jsonify(dict(status=error_code, message=msg)))


@app.errorhandler(404)
def error_404(msg=None):
    if not msg:
        msg = 'Not found'
    return make_error_response(404, msg)


@app.errorhandler(409)
def error_409(msg):
    return make_error_response(409, msg)


@app.errorhandler(400)
def error_400(msg=None):
    if not msg:
        msg = 'Invalid request'
    return make_error_response(400, msg)


@app.errorhandler(415)
def error_415(msg=None):
    if not msg:
        msg = 'Invalid media type'
    return make_error_response(415, msg)


def validate_user_data(userid, data, method):
    """Check to be sure data is structured properly and complete per
    API spec: https://gist.github.com/jakedahn/3d90c277576f71d805ed"""

    # check that all expected fields exist
    try:
        assert set(data.keys()) == set(EXPECTED_KEYS)
    except AssertionError:
        msg = 'Missing fields in user data. Expected %s'
        return error_400(msg % ', '.join(EXPECTED_KEYS))

    # check for missing data - there should be four values
    try:
        assert len([v for v in data.values() if v]) == len(EXPECTED_KEYS)
    except AssertionError:
        msg = 'Not all fields have values. Required values: %s'
        return error_400(msg % ', '.join(EXPECTED_KEYS))

    # check to be sure the userid derived from the request URL
    # matches the userid specified in the request body
    try:
        assert userid == data.get('userid')
    except AssertionError:
        uid = data.get('userid')
        msg = 'Inconsistent userid in URL & payload: %s vs. %s' % (userid, uid)
        return error_400(msg)

    # check for existence of userid in data store as appropriate for
    # POST and PUT methods.
    if method == 'POST':
        # check for duplicated userid
        if userid in USERS:
            msg = 'Conflict: username %s already exists' % userid
            return error_409(msg)

    elif method == 'PUT':
        if userid not in USERS:
            msg = 'User %s not found so cannot be updated.' % userid
            return error_404(msg)

    else:
        raise Exception('Invalid method %s' % method)

    return True


def add_user_to_groups(userid, data):
    """Add user to appropriate groups in data store."""
    groups = data['groups']
    for g in groups:
        if g in GROUPS:
            GROUPS[g].append(userid)
        else:
            GROUPS[g] = [userid]
    return True


def delete_from_groups(userid):
    """Delete user from groups in data store."""
    for g in GROUPS.keys():
        GROUPS[g] = [member for member in GROUPS[g] if member != userid]
    return True


def delete_user(userid):
    """Delete user from data store."""
    del USERS[userid]
    delete_from_groups(userid)
    return True


def add_user(userid, data, method):
    """Add user to data store if validation succeeds. If validation fails,
    return the error response object."""
    validated = validate_user_data(userid, data, method)

    # 'validated' is True if validation succeeds.
    if type(validated) is bool and validated:
        # everything checks out, so let's proceed.
        # add user
        USERS[userid] = data

        # add to groups
        add_user_to_groups(userid, data)

        # return user in response
        return jsonify(USERS[userid])

    # otherwise, return the response object
    else:
        return validated


def add_to_group(groupname, user_list):
    merged_user_list = GROUPS[groupname] + user_list
    # remove duplicate users and cast as list
    GROUPS[groupname] = list(set(merged_user_list))

    return True


def delete_group(groupname):
    """Delete group from GROUPS"""
    del GROUPS[groupname]

    return True
