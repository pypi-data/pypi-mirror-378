sgpi = float(input("Enter your SGPI: "))

if sgpi >= 9.00 and sgpi <= 10.00:
    grade = "O"
elif sgpi >= 8.00 and sgpi <= 8.99:
    grade = "A+"
elif sgpi >= 7.00 and sgpi <= 7.99:
    grade = "A"
elif sgpi >= 6.00 and sgpi <= 6.99:
    grade = "B+"
elif sgpi >= 5.00 and sgpi <= 5.99:
    grade = "B"
elif sgpi >= 4.00 and sgpi <= 4.99:
    grade = "C"
elif sgpi >= 0 and sgpi < 4.00:
    grade = "F"
else:
    grade = "Invalid SGPI"

print("Your grade is:", grade)