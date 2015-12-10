import json

from flask import Flask
from flask import request
from flask import Response
from flask.json import jsonify

import manager

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify(response='Hello World!')


@app.route('/users/<string:userid>', methods=['GET'])
def get_user(userid):
    if userid in manager.USERS:
        return jsonify(manager.USERS[userid])
    else:
        msg = 'User not found: %s' % userid
        return manager.error_404(msg)


@app.route('/users/<string:userid>', methods=['POST'])
def post_user(userid):
    return manager.add_user(userid, request.get_json(), 'POST')


@app.route('/users/<string:userid>', methods=['PUT'])
def put_user(userid):
    return manager.add_user(userid, request.get_json(), 'PUT')


@app.route('/users/<string:userid>', methods=['DELETE'])
def delete_user(userid):
    if userid in manager.USERS:
        manager.delete_user(userid)
        msg = 'Deleted user %s' % userid
        return jsonify(dict(status=200, message=msg))
    else:
        return manager.error_404('User not found: %s' % userid)


@app.route('/groups/<string:groupname>', methods=['GET'])
def get_group(groupname):
    if groupname in manager.GROUPS:
        return Response(json.dumps((manager.GROUPS[groupname])),
                        mimetype='application/json')
    else:
        return manager.error_404('Group not found: %s' % groupname)


@app.route('/groups', methods=['POST'])
def post_group():
    data = request.get_json()
    groupname = data['name']

    if groupname not in manager.GROUPS:
        manager.GROUPS[groupname] = []
        return jsonify({groupname: manager.GROUPS[groupname]})
    else:
        msg = 'Conflict: group %s already exists' % groupname
        return manager.error_409(msg)


@app.route('/groups/<string:groupname>', methods=['PUT'])
def put_group(groupname):
    if groupname in manager.GROUPS:
        user_list = request.get_json()
        manager.add_to_group(groupname, user_list)
        return jsonify({groupname: manager.GROUPS[groupname]})
    else:
        return manager.error_404('Group not found: %s' % groupname)


@app.route('/groups/<string:groupname>', methods=['DELETE'])
def delete_group(groupname):
    if groupname in manager.GROUPS:
        manager.delete_group(groupname)
        msg = 'Deleted group %s' % groupname
        return jsonify(dict(status=200, message=msg))
    else:
        return manager.error_404('Group not found: %s' % groupname)


if __name__ == '__main__':
    app.run(debug=True)
