#credit card validator using lhun's algorithm
"""Luhn Algorithm, or Modulus 10 Algorithm, is a mathematical formula that helps to determine whether 
or not a correct identification number has been provided. It is named after its creator, 
German Computer Scientist Hans Peter Luhn, who developed the Luhn Algorithm formula in 1954 during his days 
as an IBM researcher."""

#working of lhun's algorithm--
#Step 1 – Starting from the rightmost digit, double the value of every second digit, [double odd index [index starts from 0]]
#Step 2– If doubling of a number results in a two digit number i.e greater than 9(e.g., 6 × 2 = 12), then add the digits of the product (e.g., 12: 1 + 2 = 3, 15: 1 + 5 = 6), to get a single digit number. 
#Step 3-Now take the sum of all the digits.
#Step 4 – If the total modulo 10 is equal to 0 (if the total ends in zero) then the number is valid according to the Luhn formula; else it is not valid.

card=input("Enter card numebr: ")
if len(card)==16 or len(card)==19:
    odd_sum=0
    even_sum=0

    number=list(card)

    for index,x in enumerate(number):#enumerate will keep track of index value also, while for loop alone can not. index is variable
        #syntax= for inx,x in enumerate():
        if index%2==0:
            even_sum+= (int(x)*2)
        else:
            odd_sum+= int(x)

    net_sum=odd_sum+even_sum
    if net_sum%10==0:
        print("valid card")
    else:
        print("Invalid Card")
        
