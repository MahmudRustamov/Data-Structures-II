# Challenge 7 - Dynamic Array

class DynamicArray:
    def __init__(self):
        self.capacity = 2
        self.size = 0
        self.array = [None] * self.capacity

    def append(self, value):
        if self.size == self.capacity:
            self.resize()

        self.array[self.size] = value
        self.size += 1

    def resize(self):
        self.capacity *= 2
        new_array = [None] * self.capacity

        for i in range(self.size):
            new_array[i] = self.array[i]

        self.array = new_array

    def get(self, index):
        if index < 0 or index >= self.size:
            return None

        return self.array[index]

    def __str__(self):
        return str(self.array[:self.size])


arr = DynamicArray()

arr.append(10)
arr.append(20)
arr.append(30)
arr.append(40)

print(arr)
print("Size:", arr.size)
print("Capacity:", arr.capacity)