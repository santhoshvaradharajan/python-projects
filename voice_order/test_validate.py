from parse_order import validate_items

bad_case = [
    [{"name": "x", "quantity": 0}],
    [{"name": "x", "quantity": 500}],
    [{"name" : "x", "quantity" : "2"}],
    [{"name" : "x"}],
    "nope",
    ]
for bad in bad_case:
    try:
        validate_items(bad)
        print("Not caught:",bad)
    except ValueError as e:
        print("caught:", e)

validate_items([{"name" : "x", "quantity" : 2}])
print("good order parses")