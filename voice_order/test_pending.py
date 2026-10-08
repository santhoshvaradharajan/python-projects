from parse_order import save_pending, get_pending, delete_pending

save_pending("test1", [{"name" : "chicken korma", "quantity" : 2}])
print(get_pending("test1"))
delete_pending("test1")
print(get_pending("test1"))