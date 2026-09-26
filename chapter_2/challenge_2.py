def two_sum(nums, target):
    seen = {}

    for i, x in enumerate(nums):
        complement = target - x

        if complement in seen:
            return [seen[complement], i]

        seen[x] = i

    return []


nums = [2, 7, 11, 15]
target = 9

print(two_sum(nums, target))