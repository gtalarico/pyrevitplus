from random import randint
points = [PointElement(randint(0,10),randint(0,10),0) for x in range(0,30)]
pc = PointCollection()
for p in points:
    pc.points.append(p)
    # print(pc)
    print(pc.points)
    pc.sort_points('Y')
    print('='*20)
    print(pc.points)
