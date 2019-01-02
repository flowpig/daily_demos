"""
Given an array of integers, return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example:

Given nums = [2, 7, 11, 15], target = 9,

Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].
"""


import copy


class Solution:
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        nums2 = copy.deepcopy(nums)
        nums.sort()
        m = 0
        n = len(nums) - 1
        while m < n:
            if nums[m] + nums[n] > target:
                n -= 1
            elif nums[m] + nums[n] < target:
                m += 1
            else:
                tp = []
                for i in range(len(nums2)):
                    if nums2[i] == nums[m] or nums2[i] == nums[n]:
                        tp.append(i)
                return tp

