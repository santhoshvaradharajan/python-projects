def AddressVal(address):
    dot = address.find(".")
    at = address.find("@")
    com = address.find("com")

    if(dot == -1):
        print("Invalid")
    elif(at == -1):
        print("Invalid")
    else:
        print("Valid")

print("This code will check ur email address is correct or not")
while True:
    print("your email contains '@' and '.' or else it will be invalid!!")
    Email = input("what's ur email address: ")

    AddressVal(Email)    

