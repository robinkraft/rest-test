This is a simple REST service written against this spec:

https://github.com/robinkraft/rest-test/blob/master/spec.md


### Installation

```shell
pip install -r requirements.txt
```

### Run tests

```shell
nosetests tests
```

### Sample requests

Start the app: `python api/main.py`. Then run these commands in your terminal of choice.

###### Users

```shell
# see sample data
curl -i -X GET http://localhost:5000/users/jsmith

# add nmarcus user
curl -i -H "Content-Type: application/json" -X POST -d '{"first_name": "Neiman", "last_name": "Marcus", "userid": "nmarcus", "groups": ["sales", "admins"]}' http://localhost:5000/users/nmarcus

# modify nmarcus - change last name
curl -i -H "Content-Type: application/json" -X PUT -d '{"first_name": "Neiman", "last_name": "Marcus-Aurelius", "userid": "nmarcus", "groups": ["sales", "admins"]}' http://localhost:5000/users/nmarcus

# delete nmarcus
curl -i -X DELETE http://localhost:5000/users/nmarcus

# check deletion
curl -i -X GET http://localhost:5000/users/nmarcus
```

###### Groups

```shell
curl -i -X GET http://localhost:5000/groups/admins

# add musicians group
curl -i -H "Content-Type: application/json" -X POST -d '{"name": "musicians"}' http://localhost:5000/groups

# add to musicians group
curl -i -H "Content-Type: application/json" -X PUT -d '["jbach", "arose"]' http://localhost:5000/groups/musicians

# check musicians group
curl -i -X GET http://localhost:5000/groups/musicians

# delete musicians group
curl -i -X DELETE http://localhost:5000/groups/musicians

# check deletion
curl -i -X GET http://localhost:5000/groups/musicians
```
