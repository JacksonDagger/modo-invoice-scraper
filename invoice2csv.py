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
    start = line.find('Time:')
    line = line[start:]
    dollar = line.find('$')
    while dollar != -1:
        line = line[dollar+1:]
        period_i = line.find('.')
        if len(line) > period_i + 3 and (line[period_i+3] == ',' or line[period_i+3] == '.'):
            sum += float(line[:period_i+3])
        dollar = line.find('$')

    return sum


def find_next_entry(invoice_text, month):
    """
    find the next entry in the text based on previously seen text patterns
    """
    i = invoice_text.find('On ' + month)
    return i


invoice_dir = "invoices"
files = filter(lambda x : x[-4:]=='.pdf', os.listdir(invoice_dir))
df = pd.DataFrame(columns=['Date', 'Rental Company', 'Amount'])
dfi = 0 # index to add to in df

for f in files:
    fname = os.path.join(invoice_dir, f)

    with open(fname,'rb') as invoice: # open invoice
        invoice_pdf = slate.PDF(invoice)
    invoice_text = str(invoice_pdf)
    invoice_text = invoice_text.replace('\\n', '\n ') # clean up newlines
    invoice_text = invoice_text.replace('\n \n ', '\n ')

    search_text = invoice_text

    """
    fr = open('test.txt', 'w') # tracking what the program is seeing
    fr.write(invoice_text)
    fr.close()
    """

    booking_index = invoice_text.find('bookings this month.')
    num_bookings = int(invoice_text[booking_index-4:booking_index].split(' ')[-2])

    data_start = invoice_text.find('usage details') # month of invoice is listed here
    month_str = invoice_text[:data_start].split(' ')[-3:-1]
    month = month_str[0]
    year = month_str[1]
    invoice_text = invoice_text[data_start:] # no ride data before this

    i = find_next_entry(invoice_text, month) # find the standard form of a Modo statement

    while i != -1:
        invoice_text = invoice_text[i:]
        month_pos = invoice_text.find(month)
        year_pos = invoice_text.find(year)
        time_pos = invoice_text[year_pos+4].find(':')
        date = dateparser(invoice_text[month_pos:year_pos+4] + ' ' +
        invoice_text[time_pos -2 : time_pos +3])
        date = date.date()

        split = invoice_text.find('PST') + 12
        if 'PVRT' in invoice_text[split: split + 65]:
            split = invoice_text[split: split + 65].find('PVRT') + 18
        readline = invoice_text[:split] # collect only the line that this statement is for
        invoice_text = invoice_text[split-3:] # remove the statement we've already found

        cost = get_money(readline)
        cost = "%.2f" % round(cost, 2)

        if "$" + cost not in search_text:
            print(cost + " seems to be wrong in " + f + " on " + str(date))
        if float(cost)<1.0:
            print(cost + " seems to be wrong in " + f + " on " + str(date))

        late_return_str = "Charge for late return"
        late_return_i = search_text.find(late_return_str)
        while late_return_i != -1:
            end_late_line = search_text[late_return_i:].find('\n')
            print("Late return: " + search_text[late_return_i: late_return_i + end_late_line] + " in  " + f)
            search_text = search_text[late_return_i + len(late_return_str):]
            late_return_i = search_text.find(late_return_str)
        df.loc[dfi] = [date, 'Modo', cost]
        dfi += 1 # write to next row

        i = find_next_entry(invoice_text, month) # find the standard form of a Modo statement
        num_bookings -= 1

    if num_bookings != 0:
        print(str(num_bookings) + " bookings off by in " + f)

df.to_csv('modo_usage.csv', index=False)
