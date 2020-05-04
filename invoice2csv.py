import slate3k as slate
import pandas as pd
import os
from dateutil.parser import parse as dateparser

def get_money(line):
    """
    returns the sum of all dollar values (printed in the format ""$x.xx")
    in the given string
    """
    sum = 0.0
    dollar = line.find('$')
    while dollar != -1:
        line = line[dollar+1:]
        sum += float(line[:line.find('.')+3])
        dollar = line.find('$')

    return sum


invoice_folder = "invoices"

fname = os.path.join(invoice_folder, "Modo Invoice #1576995.pdf")

with open(fname,'rb') as invoice: # open invoice
    invoice_pdf = slate.PDF(invoice)
invoice_text = str(invoice_pdf)
invoice_text = invoice_text.replace('\\n', '\n ') # clean up newlines
invoice_text = invoice_text.replace('\n \n ', '\n ')

fr = open('test.txt', 'w') # tracking what the program is seeing
fr.write(invoice_text)
fr.close()

data_start = invoice_text.find('usage details') # month of invoice is listed here
month_str = invoice_text[:data_start].split(' ')[-3:-1]
month = month_str[0]
year = month_str[1]
invoice_text = invoice_text[data_start:] # no ride data before this

i = invoice_text.find('On ' + month) # find the standard form of a Modo statement

while i != -1:
    invoice_text = invoice_text[i:]
    date = dateparser(invoice_text[invoice_text.find(month):invoice_text.find(year)+4])

    parts = invoice_text.split('.\n', 1)
    readline = parts[0] # collect only the line that this statement is for
    invoice_text = parts[1] # remove the statement we've already found

    cost = get_money(readline)

    i = invoice_text.find('On ' + month)
    print(str(cost))
    #print(str(date))
