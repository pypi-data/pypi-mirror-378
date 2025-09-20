# DictOfLists & DictOfSets

This package is designed to simplify code when **all the values of a dictionary are intended to be `list` or `set` objects**.

## DictOfLists
If a key does not exist, it will automatically be initialized with an **empty list**.

## DictOfSets
If a key does not exist, it will automatically be initialized with an **empty set**.

---

By using these two dictionary types, there is **no need to manually check for key existence** or to add an empty list or set as its value throughout your code.  
These actions are handled **automatically** whenever a key is accessed.
