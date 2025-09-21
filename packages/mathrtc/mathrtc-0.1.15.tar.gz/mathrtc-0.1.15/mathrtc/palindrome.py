def palindrome():
    a = input("Enter the Word :")
    b = a[::-1]
    if a == b:
        print("It's palindrome")
    else:
        print("It's not palindrome")