player_name = input("Enter your name: ")

hp = 100
max_hp = 100
xp = 0
level = 1
potions = 3
gold = 50
atk = 1


while True:

    print()
    print("=== MAIN MENU ===")
    print("1. View Character")
    print("2. Go on Quest")
    print("4. Visit Shop")
    print("3. Exit Game")

    choice = input("Choose: ")

    # CHARACTER
    if choice == "1":

        print()
        print("=== CHARACTER ===")
        print("Name:", player_name)
        print("HP:", hp, "/", max_hp)
        print("XP:", xp)
        print("Level:", level)
        print("Gold:", gold)
        print("Potions:", potions)
        print("ATK:", atk)

    # QUEST
    elif choice == "2":

        print()
        print("=== QUEST ===")
        print("1. Fight Goblin")
        print("2. Fight Skeleton")
        print("3. Fight Dragon")
        print("4. Exit Quest")

        quest = input("Choose: ")

        if quest == "1":

            enemy_hp = 30
            enemy_atk = 5

            print()
            print("A Goblin appeared!")

            while enemy_hp > 0 and hp > 0:

                print()
                print("Your HP:", hp)
                print("Goblin HP:", enemy_hp)
                print("1. Attack")
                print("2. Use Potion")
                print("3. Run")

                action = input("Choose: ")

                if action == "1":

                    enemy_hp -= atk * 10

                    if enemy_hp > 0:
                        hp -= enemy_atk
                        print("The Goblin attacked you!")
                    else:
                        print("You killed the Goblin!")
                        xp += 20
                        gold += 50
                        print("+20 XP")
                        print("+50 Gold")

                elif action == "2":

                    if potions > 0:

                        hp += 20

                        if hp > max_hp:
                            hp = max_hp

                        potions -= 1

                        print("You used a Health Potion!")
                        print("HP:", hp)

                    else:
                        print("You don't have any potions!")

                elif action == "3":

                    print("You ran away!")
                    break

                else:
                    print("Invalid choice!")

        elif quest == "2":

            enemy_hp = 50
            enemy_atk = 10

            print()
            print("A Skeleton appeared!")

            while enemy_hp > 0 and hp > 0:

                print()
                print("Your HP:", hp)
                print("Skeleton HP:", enemy_hp)
                print("1. Attack")
                print("2. Use Potion")
                print("3. Run")

                action = input("Choose: ")

                if action == "1":

                    enemy_hp -= atk * 10

                    if enemy_hp > 0:
                        hp -= enemy_atk
                        print("The Skeleton attacked you!")
                    else:
                        print("You killed the Skeleton!")
                        xp += 40
                        gold += 100
                        print("+40 XP")
                        print("+100 Gold")

                elif action == "2":

                    if potions > 0:

                        hp += 20

                        if hp > max_hp:
                            hp = max_hp

                        potions -= 1

                        print("You used a Health Potion!")
                        print("HP:", hp)
                    else:
                        print("You don't have any potions!")

                elif action == "3":

                    print("You ran away!")
                    break

                else:
                    print("Invalid choice!")
        elif quest == "3":

            enemy_hp = 100
            enemy_atk = 20

            print()
            print("A Dragon appeared!")

            while enemy_hp > 0 and hp > 0:

                print()
                print("Your HP:", hp)
                print("Dragon HP:", enemy_hp)
                print("1. Attack")
                print("2. Use Potion")
                print("3. Run")

                action = input("Choose: ")

                if action == "1":

                    enemy_hp -= atk * 10

                    if enemy_hp > 0:
                        hp -= enemy_atk
                        print("The Dragon attacked you!")
                    else:
                        print("You killed the Dragon!")
                        xp += 100
                        gold += 500
                        print("+100 XP")
                        print("+500 Gold")

                elif action == "2":

                    if potions > 0:

                        hp += 20

                        if hp > max_hp:
                            hp = max_hp

                        potions -= 1

                        print("You used a Health Potion!")
                        print("HP:", hp)

                    else:
                        print("You don't have any potions!")

                elif action == "3":

                    print("You ran away!")
                    break

                else:
                    print("Invalid choice!")
        if hp <= 0:
            print()
            print("💀 You died!")
            print("Game Over!")
            break

        # LEVEL UP

        if xp >= level * 100:

            level += 1
            max_hp += 20
            hp = max_hp
            atk += 1

            print()
            print("🎉 LEVEL UP!")
            print("You are now level", level)
            print("+20 Max HP")
            print("+1 ATK")

    # SHOP
    elif choice == "4":

        while True:

            print()
            print("=== SHOP ===")
            print("Gold:", gold)
            print("Potions:", potions)
            print("1. Health Potion - 10 Gold")
            print("2. Sword Upgrade - 20 Gold")
            print("3. Exit Shop")

            shop_choice = input("Choose: ")

            if shop_choice == "1":

                if hp >= max_hp:
                    potions += 1
                    gold -= 10
                    print("You bought a Health Potion!")
                elif gold >= 10:
                    gold -= 10
                    hp += 20
                    if hp > max_hp:
                        hp = max_hp

                    print("You bought a Health Potion!")
                    print("HP:", hp)
                else:
                    print("Not enough gold!")

            elif shop_choice == "2":

                if gold >= 20:

                    gold -= 20
                    atk += 1

                    print("You upgraded your sword!")
                    print("ATK:", atk)

                else:
                    print("Not enough gold!")

            elif shop_choice == "3":

                print("Leaving shop...")
                break

            else:
                print("Invalid choice!")

    # EXIT
    elif choice == "3":

        print("Thanks for playing!")
        break

    else:

        print("Invalid choice!")
