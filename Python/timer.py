import time
my_time = input("Enter the time in seconds: ")
my_time = int(my_time)

for count in range(my_time, 0, -1):
    seconds = count % 60
    minutes = count // 60 % 60
    hours = count // 3600
    print(f"{hours:02}:{minutes:02}:{seconds:02}")
    time.sleep(1)
print("Time's up!")
