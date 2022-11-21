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

print('\nListing all assets with dot notation: category.asset')
print('m1:', list(m1))
print('m2:', list(m2))
print('m (m1+m2):', list(m))
# m1: ['System.Host', 'System.Network', 'System.Password', 'System.User']
# m2: ['C2.A1', 'C2.A2', 'C2.A3', 'C2.A4', 'C2.A5', 'C2.A6', 'C3.A1', 'C4.A1', 'C5.distribution']
# m (m1+m2): ['System.Host', 'System.Network', 'System.Password', 'System.User', 'C2.A1', 'C2.A2', 'C2.A3', 'C2.A4', 'C2.A5', 'C2.A6', 'C3.A1', 'C4.A1', 'C5.distribution']