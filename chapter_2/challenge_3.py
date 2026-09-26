class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


def reverse(head):
    prev = None
    curr = head

    while curr is not None:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev


head = Node(1)
head.next = Node(2)
head.next.next = Node(3)

head = reverse(head)

curr = head

while curr is not None:
    print(curr.data, end=" → ")
    curr = curr.next

print("None")