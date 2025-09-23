You can use any commonly used constants like pi, e, h(plancks constant), avogadro number, etc.
syntax:
#on first line of code
from constants import values as vals #as vals part is your choice
#then
print(f"{vals.pi} {vals.h} {vals.e}")
#output:
3.14 6.626e-34 2.71828 #e is exponent here not constant e (euler)


in this module there is on another file also, name functions where you can use 4 different functions for now named as getin, ou, Greater_among_two, Greates_Among_Three
syntax:
from constants import functions as fn
a = fn.getin("Enter any number: ") #getin is used in place of input()
b = fn.getin("Enter any number: ")
c = fn.getin("Enter any number: ")
gtwo = fn.Greater_among_two(a, b)
gthree = fn.Greatest_Among_Three(a, b, c)
#out is used in place of print
fn.out(f"Greatest among {a} and {b} is {gtwo}")
fn.out(f"Greatest ampng {a}, {b} and {c} is {gthree}")