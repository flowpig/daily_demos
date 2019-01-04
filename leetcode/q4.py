"""
There are two sorted arrays nums1 and nums2 of size m and n respectively.

Find the median of the two sorted arrays. The overall run time complexity should be O(log (m+n)).

You may assume nums1 and nums2 cannot be both empty.

Example 1:

nums1 = [1, 3]
nums2 = [2]

The median is 2.0
Example 2:

nums1 = [1, 2]
nums2 = [3, 4]

The median is (2 + 3)/2 = 2.5
"""


class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        m = len(nums1)
        n = len(nums2)
        temp = []
        i = 0
        j = 0
        while i < m and j <n:
            if nums1[i] <= nums2[j]:
                temp.append(nums1[i])
                i += 1
            else:
                temp.append(nums2[j])
                j += 1
        if i < m:
            temp.extend(nums1[i:])
        if j < n:
            temp.extend(nums2[j:])
        print(temp)
        r = int((m + n - 1) / 2)
        if (m + n) % 2 == 0:
            return (temp[r] + temp[r+1])/2
        return temp[r]


if __name__ == '__main__':
    nums1 = [1, 3]
    nums2 = [2, 4]
    obj = Solution()
    print(obj.findMedianSortedArrays(nums1, nums2))