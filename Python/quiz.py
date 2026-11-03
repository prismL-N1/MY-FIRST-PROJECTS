print("         QUIZ          ")
score = 0

# 1 first question

answer = int(input("1. whats 15 x 4?  "))
if answer == 60:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 2 second question

answer = int(input("2. whats 20+20?  "))
if answer == 40:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 3 third question

answer = int(input("3. whats 25-10?  "))
if answer == 15:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 4 fourth question

answer = int(input("4. whats 30/6?  "))
if answer == 5:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 5 fifth question

answer = int(input("5. whats 10 x 10?  "))
if answer == 100:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 6 sixth question

answer = int(input("6. whats 50-25?  "))
if answer == 25:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 7 seventh question

answer = int(input("7. whats 100/4?  "))
if answer == 25:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 8 eighth question

answer = int(input("8. whats 5 x 5?  "))
if answer == 25:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 9 ninth question

answer = int(input("9. whats 12+12?  "))
if answer == 24:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

# 10 tenth question

answer = int(input("10. whats 100-50?  "))
if answer == 50:
    print("thats wright")
    score = score + 1
else:
    print("thats wrong")

print(f"congratulations! you got {score} out of 10 questions right")
