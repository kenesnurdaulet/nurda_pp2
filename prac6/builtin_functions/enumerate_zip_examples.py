names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate
for i, name in enumerate(names):
    print(i, name)

# zip
for name, score in zip(names, scores):
    print(name, score)

# sorted
nums = [5, 2, 9, 1]
print(sorted(nums))

# type conversion
x = "123"
print(int(x))
print(float(x))
print(str(456))