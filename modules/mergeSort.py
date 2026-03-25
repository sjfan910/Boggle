"""
MergeSort class used across multiple modules.
Sorting algorithm is implemented from scratch rather than using Python's built-in sort.

MergeSort Class:
Key Methods:
 - sort(lst):
        - Static method — no instance needed, called as MergeSort.sort(lst)
        - Recursive in-place merge sort of time complexity O(n log n)
        - Accepts any list whose elements support <= comparison (strings, integers, etc.)
        - Divides the list into two halves
        - Recursively sorts each half
        - Merges the two sorted halves back into the original list in order
"""

class MergeSort:
    @staticmethod
    def sort(lst):
        # Recursive In Place Merge Sort of Time complexity O(nlog(n))
        n = len(lst)
        if n > 1:
            m = n // 2  # divide the list in two sub lists
            l1 = lst[:m]
            l2 = lst[m:]

            MergeSort.sort(l1)
            MergeSort.sort(l2)

            i = j = k = 0

            while i < len(l1) and j < len(l2):
                if l1[i] <= l2[j]:
                    lst[k] = l1[i]
                    i += 1
                else:
                    lst[k] = l2[j]
                    j += 1
                k = k + 1

            while i < len(l1):
                lst[k] = l1[i]
                i += 1
                k += 1
            while j < len(l2):
                lst[k] = l2[j]
                j += 1
                k += 1
