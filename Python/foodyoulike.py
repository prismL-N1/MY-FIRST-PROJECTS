food = input("what food do you like (q to quit)")

while not food == "q":
    print(f"you like {food}")
    food = input("what other food do you like (q to quit)")
print("Thanks for sharing your food preferences!")
