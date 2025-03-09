list1 = [1,2,3,2]
other = [2,3,4]
newlist = []
if len(list1) != len(other):
    print(max((len(list1)), len(other)))
    list1 += [0] * (max((len(list1)), len(other)) - len(list1))
    other += [0] * (max((len(list1)), len(other)) - len(other))
    print(list1)
    print(other)
    # if len(list1) > len(other):
    #     missing = len(list1) - len(other)
    #     for i in range(missing):
    #         other.append(0)
    # elif len(list1) < len(other):
    #     missing = len(other) - len(list1)
    #     for i in range(missing):
    #         list1.append(0)
for i in range(len(list1)):
    # print(i)
    newlist.append(list1[i] * other[i])

print(f",".join([str(i) for i in newlist]))
