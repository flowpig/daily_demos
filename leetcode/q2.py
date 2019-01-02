"""
You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order and each of their nodes contain a single digit. Add the two numbers and return it as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Example:

Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 0 -> 8
Explanation: 342 + 465 = 807.
"""


# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        result = None
        temp = None
        flag = 0
        while l1 or l2:
            if not l1:
                val = 0 + l2.val + flag
            elif not l2:
                val = l1.val + 0 + flag
            else:
                val = l1.val + l2.val + flag
            flag = val // 10

            node = ListNode(val % 10)
            if result:
                temp.next = node
            else:
                result = node
            temp = node
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        if flag == 1:
            temp.next = ListNode(1)
        return result


#if __name__ == '__main__':
#    la = ListNode(2)
#    la.next = ListNode(4)
#    la.next.next = ListNode(3)
#    lb = ListNode(5)
#    lb.next = ListNode(6)
#    lb.next.next = ListNode(4)
#    obj = Solution()
#    res = obj.addTwoNumbers(la, lb)
#    print(res.next.next.val)

