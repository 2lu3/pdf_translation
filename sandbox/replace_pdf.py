from pypdf import PdfReader

reader = PdfReader("test.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
print(text)

#from pdfminer.high_level import extract_text
#
#text = extract_text('./test.pdf')
#
#print(repr(text))



#doc = fitz.Document("./test.pdf")
#
#for page in doc:
#    for link in page.links():
#        print(link)
