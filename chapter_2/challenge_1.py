def check_brackets(s):
    stack = []

    pairs = {
        ')': '(',
        ']': '[',
        '}': '{'
    }

    for i, char in enumerate(s):

        if char in "([{":
            stack.append((char, i))

        elif char in ")]}":

            if not stack:
                return False, i

            opening, index = stack.pop()

            if opening != pairs[char]:
                return False, i

    if stack:
        return False, stack[-1][1]

    return True

print(check_brackets("()"))
print(check_brackets("(]"))