"""
Given a string, find the length of the longest substring without repeating characters.

Example 1:

Input: "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3.
Example 2:

Input: "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.
Example 3:

Input: "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3.
             Note that the answer must be a substring, "pwke" is a subsequence and not a substring.
"""


# 借鉴他人的solution
class Solution:
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        idx, n, start, res = [0] * 128, len(s), 0, 0
        for i in range(n):
            start = max(start, idx[ord(s[i])])
            res = max(res, i - start + 1)
            idx[ord(s[i])] = i + 1
        return res


# 未能AC， Time Limit Exceeded
class Solution01:
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        if len(s) <= 1:
            return len(s)
        temp = []
        length_li = []
        count = 0
        while count < len(s):
            for c in s[count:]:
                if c not in temp:
                    temp.append(c)
                else:
                    length = len(temp)
                    length_li.append(length)
                    temp.clear()
                    break
            count += 1
        return max(length_li)


# 未能AC， Time Limit Exceeded
class Solution02:
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        if len(s) <= 1:
            return len(s)
        max_li = []
        count = 0
        while count < len(s):
            temp = []
            for c in s[count:]:
                if c not in temp:
                    temp.append(c)
                else:
                    max_li = temp if len(temp) >= len(max_li) else max_li
                    temp = [c]
            max_li = max_li if len(max_li) >= len(temp) else temp
            count += 1
        return len(max_li)


if __name__ == '__main__':
    obj = Solution()
    s = "abcasdasd"
    print(obj.lengthOfLongestSubstring(s))