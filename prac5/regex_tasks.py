import re


# 1. Match 'a' followed by zero or more 'b'

pattern1 = r"ab*"
print("1:", re.findall(pattern1, "a ab abb abbb ac"))



# 2. Match 'a' followed by 2 to 3 'b'

pattern2 = r"ab{2,3}"
print("2:", re.findall(pattern2, "ab abb abbb abbbb"))



# 3. Find lowercase words joined with underscore

pattern3 = r"\b[a-z]+_[a-z]+\b"
print("3:", re.findall(pattern3, "hello_world test_value Hello_World"))



# 4. Find sequences of one uppercase letter followed by lowercase letters

pattern4 = r"\b[A-Z][a-z]+\b"
print("4:", re.findall(pattern4, "Hello world Test Python PYTHON"))


# 5. Match 'a' followed by anything, ending with 'b'

pattern = r"a[^ ]*b"
print(re.findall(pattern, "acb a123b afc axxxb"))



# 6. Replace space, comma, or dot with colon

text6 = "Hello, world. Python is cool"
result6 = re.sub(r"[ ,.]", ":", text6)
print("6:", result6)



# 7. Convert snake_case to camelCase

def snake_to_camel(text):
    return re.sub(r"_([a-z])", lambda x: x.group(1).upper(), text)

print("7:", snake_to_camel("hello_world_test"))


# 8. Split a string at uppercase letters


text8 = "HelloWorldTest"
result8 = [x for x in re.split(r"(?=[A-Z])", text8) if x]
print("8:", result8)



# 9. Insert spaces between words starting with capital letters

text9 = "HelloWorldTest"
result9 = re.sub(r"([A-Z])", r" \1", text9).strip()
print("9:", result9)



# 10. Convert camelCase to snake_case

def camel_to_snake(text):
    return re.sub(r"([A-Z])", r"_\1", text).lower()

print("10:", camel_to_snake("helloWorldTest"))