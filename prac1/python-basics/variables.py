# variables.py
# Python Variables examples
# 1)Simple variables
x = 5
y = "John"
print(x)
print(y)


# 2)Changing variable type
x = 4 #int
x = "Sally" #str
print(x)


print(x)

print("-----")

# 3)Case-sensitive variables
a = 4
A = "Sally"
print(a)
print(A)

print("-----")

# 4) Valid variable names
myvar = "John"
my_var = "John"
_my_var = "John"
myVar = "John"
MYVAR = "John"
myvar2 = "John"
print(myvar, my_var, _my_var, myVar, MYVAR, myvar2)

print("-----")

# 5) Multiple assignment
x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

print("-----")

# 6) One value to multiple variables
x = y = z = "Orange"
print(x)
print(y)
print(z)

print("-----")

# 7) Unpacking a list
fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)

print("-----")

# 8) Global variable (read)
x = "awesome"

def myfunc():
    print("Python is " + x)

myfunc()

print("-----")

# 9) Local variable inside function
x = "awesome"

def myfunc():
    x = "fantastic"
    print("Python is " + x)

myfunc()
print("Python is " + x)

print("-----")

# 10) global keyword (change global variable)
x = "awesome"

def myfunc():
    global x
    x = "fantastic"

myfunc()
print("Python is " + x)