import slate3k as slate
import pandas as pd


fname = "Modo Invoice #1576995.pdf"

with open(fname,'rb') as invoice:
    invoice_pdf = slate.PDF(invoice)
invoice_text = str(invoice_pdf)
invoice_text = invoice_text.replace('\\n', '\n')
invoice_text = invoice_text.replace('\n\n', '\n')

fr = open('test.txt', 'w')
fr.write(invoice_text)
fr.close()
