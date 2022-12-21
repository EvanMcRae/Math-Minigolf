from math import sin
import parser

formula = "x+1"
code = parser.expr(formula).compile()
x = 10
#print(eval(code))

# importing "cmath" for complex number operations
import cmath

# Initializing real numbers
x = 5
y = 3

# converting x and y into complex number
z = complex(x,y)
z = complex("2+j")

print(z)

z += 10

#print(z)