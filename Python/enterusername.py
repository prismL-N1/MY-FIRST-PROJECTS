# a = int(input("Enter the length of the rectangle: "))
# b = int(input("Enter the width of the rectangle: "))
# c = a * b
# print("The area of the rectangle is:", c)
username = input("Enter your username: ")
while len(username) > 12:
    username = input(
        "Username is too long. Please enter a username with 12 characters or less.")
while " " in username:
    username = input(
        "Username must not contain any spaces. Please enter a different username: ")
while "1" in username or "2" in username or "3" in username or "4" in username or "5" in username or "6" in username or "7" in username or "8" in username or "9" in username or "0" in username:
    username = input(
        "Username must not contain any numbers. Please enter a different username: ")

print("Your username is valid")
