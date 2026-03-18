from functools import reduce

nums = [1, 2, 3, 4, 5]

# map
squared = list(map(lambda x: x**2, nums))
print(squared)

# filter
even = list(filter(lambda x: x % 2 == 0, nums))
print(even)

# reduce
total = reduce(lambda x, y: x + y, nums)
print(total)