import random
r = int
random_number = random.randint(1, 11)

print("მე ჩავიფიქრე რიცხვი 1 დან 10 მდე და შენ უნდა გამოიცნო")

while r != random_number:
    r = int(input("შენი ვარაუდი: "))
    if r < random_number:
        print("ჩემი რიცხვი უფრო მაღალია")
    elif r > random_number:
        print("ჩემი რიცხვი უფრო დაბალია")
    else:
        print("გილოცავ! გამოიცანი ჩემი რიცხვი")
