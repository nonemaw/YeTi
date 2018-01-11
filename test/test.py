class solution:
    @staticmethod
    def test(nums):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        if len(nums) < 3:
            return []

        result = []
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                remain = -(nums[i] + nums[j])
                if remain in nums[j::]:
                    result.append([nums[i], nums[j], remain])

        return result


print(solution.test([3,0,-2,-1,1,2]))