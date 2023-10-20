import locale

# locale.setlocale(locale.LC_ALL, '')
# string = "10/03/2023 $40,840.99\n10/02/2023 $46,170.47\n10/01/2023 $39,901.99"
# tmp = string.split('\n')
# d = dict()
# for i in tmp:
#     arr = i.split(' ')
#     d[arr[0]] = float(locale.atof(arr[1].strip('$')))
# print(d)
string = 'Emmanuel St Amour completed Open Oil GSR English and Espanol'
x = string.split(' completed ')
print(x)