import random

mx = []


# testy statystyczne w próbie Bernouliego

for _ in range(1000):
    mx.append(sum([random.randint(0,1) for _ in range(10000)]))

print(max(mx))