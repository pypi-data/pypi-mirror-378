num = int(input("Enter a number: "))

def is_armstrong(n):
    digits = str(n)
    power = len(digits)
    total = sum(int(digit)**power for digit in digits)
    return total == n

def is_palindrome(n):
    return str(n) == str(n)[::-1]

if is_armstrong(num):
    print(f"{num} is an armstrong num")
else:
    print(f"{num} is not an armstrong num")

if is_palindrome(num):
    print(f"{num} is a palindrome")
else:
    print(f"{num} is not a palindrome")