# First & Last Position

def find_first(nums, target):
    left = 0
    right = len(nums) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            result = mid
            right = mid - 1

        elif nums[mid] < target:
            left = mid + 1

        else:
            right = mid - 1

    return result


def find_last(nums, target):
    left = 0
    right = len(nums) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            result = mid
            left = mid + 1

        elif nums[mid] < target:
            left = mid + 1

        else:
            right = mid - 1

    return result


def first_last(nums, target):
    return [find_first(nums, target),
            find_last(nums, target)]


nums = [1, 2, 2, 2, 3, 4]

print(first_last(nums, 2))