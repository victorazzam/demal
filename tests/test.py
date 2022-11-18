import json
from demal import MalParser

print('Parsing two test files and combining their results.')
m1, m2 = MalParser('test1.mal'), MalParser('test2.mal')
m1.parse() ; m2.parse()

print('First:', m1['version'])
# First: 1.0.0

print('Second:', m2['version'])
# Second: 0.0.0

m = m1 + m2 # combine category/association items, same as "include"
print('Combined:', m['version'])
# Combined: 0.0.0

print('\nModifying a single variable.')
v = {'version': '1.3.3.7'}
m += v
print('New version:', m['version'])
# New version: 1.3.3.7

print('\nChanging inner dictionary data.')
var = m['categories']['System']['assets']['Host']['attributes']['guessedPassword']['probability']
print('Before:', var)
# Before: Exponential(0.02)

var = 'abc' # directly modify data
print('After:', var)
# After: abc

print('\nListing all categories, associations, and major keys/variables.')
print(list(m))
# ['id', 'version', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'System', 'A', 'Credentials', 'I2', 'I5', 'NetworkAccess']
