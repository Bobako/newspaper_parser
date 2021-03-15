import openpyxl



def save_article(article,sheet):
    
    sheet.append([article['name'],article['datetime'],article['category'],article['text']])
    
def save_all(articles,filename = 'test.xlsx',sheetname = 'test_sheet'):
    wb = openpyxl.load_workbook(filename = filename)
    sheet = wb[sheetname]
    for article in articles:
        if article!=False:
       	    save_article(article,sheet)

    wb.save(filename)


def save_ar(article, filename = 'test.xlsx', sheetname = 'test_sheet'):
    book = openpyxl.load_workbook(filename = filename)
    sheet = book[sheetname]
    sheet.append([article['name'],article['datetime'],article['category'],article['text']])
    book.save(filename)
    
