import re
import os
import sqlite3
import urllib.request as r
from bs4 import BeautifulSoup as Soup
import xlsxwriter
from collections import Counter


print("#"*70)
print("#"*70)
print("##    @@@  @@@  @@@       @@@  @@@  @@@  @    @ @  @@@  @@@  @@@    ##")
print("##    @    @    @ @       @ @  @ @  @ @  @    @ @  @    @    @ @    ##")
print("##    @@@  @@@  @ @       @@@  @ @  @@@  @    @@@  @@@  @@@  @@     ##")
print("##      @  @    @ @       @ @  @ @  @ @  @      @    @  @    @ @    ##")
print("##    @@@  @@@  @@@       @ @  @ @  @ @  @@@  @@@  @@@  @@@  @ @    ##")
print("#"*70)
print("#"*70)


# getting current working directory using os module to create a xlsx file and a database file

current_dir = os.getcwd()

# defining a function to load the url file and returning  a list of urls


def file_data():
    try:
        f = open(current_dir+"/url.txt", "r")
        f_data = f.readlines()
        f.close()
        return f_data
    except FileNotFoundError:
        print("[+]-url.text not found in current working directory")
        file_location = input("[+]-enter the location of url.txt, (eg:D://url.txt) :")
        f = open(file_location, "r")
        fl_data = f.readlines()
        f.close()
        return fl_data

# defining a function to check if the url is valid or not


def url_checker(url):
    reg = re.compile("http[://|s://]")
    match = reg.match(url)
    if match:
        print("[+]-"+name_url+" is valid..")
        return True
    else:
        print("[+]-"+name_url+" is invalid.....")


db_table_name = []


def web_data(url):

    try:
        # opening the url and scraping the web content using beautifulsoup

        req = r.Request(url, data=None, headers={'User-Agent':'Mozila/5.0(Macintosh;intel Mac OS X 10_9_3)Apple WebKit/537.36(KHTML,like Gecko)Chrome/35.0.1916.47 Safari/537.36'})
        fh = r.urlopen(req)
        wb_data = fh.read()

        # parsing the data in html format

        soup_data = Soup(wb_data, "html.parser")

        wb_str = soup_data.title.string
        wb = wb_str.split()
        wb_name = wb[0] + wb[1]

        # extracting the script and style sheet from the web content

        for script in soup_data(["script", "style"]):
            script.extract()

        # getting the text from the web content using get_text method

        text = soup_data.get_text()
        word_list = text.split()

        # defining a function to load the ignore.txt file and returning a set of ignorable words

        def ignore_list():
            try:
                ignore_file = open(current_dir+"/ignore.txt", "r")
                ig_data = ignore_file.read()
                ig_list = ig_data.split()
                ig_set = set(ig_list)
                return ig_set
            except FileNotFoundError:
                print("[+]-ignore.txt not found in current directory..")
                user_input = input("[+]-please enter the location of ignore.txt:")
                ignore_file = open(user_input, "r")
                ig_data = ignore_file.read()
                ig_list = ig_data.split()
                ig_set = set(ig_list)
                return ig_set
        ignoreset = ignore_list()

        # adding words to an empty dictionary along with their frequencies, while ignoring the ignorable words

        dic = {}
        for word in word_list:
            if word not in ignoreset:
                if word not in dic:
                    dic[word] = 1
                else:
                    dic[word] += 1

        # defining a function to count a total number of words

        def total_words():
            t_words = 0
            for wrd in word_list:
                if wrd not in ignoreset:
                    t_words += 1
            return t_words

        totalwords = total_words()

        # defining a function for density

        def wd_density(frequency):
            d = frequency/totalwords
            den = d*100
            density = int(den+0.5)
            return density

        # sorting out top5 words with a higher frequency

        sorted_list = list(Counter(dic).most_common(5))
        d1 = [sorted_list[0][0], sorted_list[0][1], wd_density(sorted_list[0][1])]
        d2 = [sorted_list[1][0], sorted_list[1][1], wd_density(sorted_list[1][1])]
        d3 = [sorted_list[2][0], sorted_list[2][1], wd_density(sorted_list[2][1])]
        d4 = [sorted_list[3][0], sorted_list[3][1], wd_density(sorted_list[3][1])]
        d5 = [sorted_list[4][0], sorted_list[4][1], wd_density(sorted_list[4][1])]

        wrkbook_data = [[d1[0], d2[0], d3[0], d4[0], d5[0]],
                        [d1[1], d2[1], d3[1], d4[1], d5[1]],
                        [d1[2], d2[2], d3[2], d4[2], d5[2]]]

        print("[+]-Creating workbook for "+name_url)
        workbook = xlsxwriter.Workbook(current_dir+"/"+wb_name+".xlsx")
        print("[+]-adding worksheet to the created workbook for "+name_url)
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        workbook.add_format({"bold": True})
        heading = ['Words', 'Frequency', 'Density']

        worksheet.write_row('A1', heading)
        worksheet.write_column('A2', wrkbook_data[0])
        worksheet.write_column('B2', wrkbook_data[1])
        worksheet.write_column('C2', wrkbook_data[2])

        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({'name': '=Sheet1!$B$1',
                          'categories': '=Sheet1!$A$2:$A$7',
                          'values': '=Sheet1!$B$2:$B$7'})

        chart.add_series({'name': ['Sheet1', 0, 2],
                          'categories': ['Sheet1', 1, 0, 6, 0],
                          'values': ['Sheet1', 1, 2, 6, 2]})

        chart.set_title({'name': 'Result of seo analysis'})
        chart.set_x_axis({'name': 'test number'})
        chart.set_y_axis({'name': 'top words'})

        chart.set_style(30)
        print("[+]-inserting chart for "+name_url)
        worksheet.insert_chart('D2', chart, {'x_offset': 150, 'y_offset': 50})
        workbook.close()
        print("[+]-worksheet created successfully for "+name_url)

        # udate sql database
        db_name = current_dir+"/seo_analyser"
        # creating sql database
        try:
            conn = sqlite3.connect(db_name+'.db')
            print("[+]-database connected")

            # creating table

            conn.execute("CREATE TABLE "+wb_name+"(WORDS TEXT, FREQUENCY INT, DENSITY INT);")
            conn.commit()

            print("[+]-table created successfully for "+name_url)

            # inserting the values

            curr = conn.cursor()
            print("[+]-inserting values into database for "+name_url)
            curr.execute("INSERT INTO "+wb_name+"(WORDS, FREQUENCY, DENSITY) VALUES(?,?,?)", (d1[0], d1[1], d1[2]))
            curr.execute("INSERT INTO "+wb_name+"(WORDS, FREQUENCY, DENSITY) VALUES(?,?,?)", (d2[0], d2[1], d2[2]))
            curr.execute("INSERT INTO "+wb_name+"(WORDS, FREQUENCY, DENSITY) VALUES(?,?,?)", (d3[0], d3[1], d3[2]))
            curr.execute("INSERT INTO "+wb_name+"(WORDS, FREQUENCY, DENSITY) VALUES(?,?,?)", (d4[0], d4[1], d4[2]))
            curr.execute("INSERT INTO "+wb_name+"(WORDS, FREQUENCY, DENSITY) VALUES(?,?,?)", (d5[0], d5[1], d5[2]))

            # saving changes and closing  the database

            conn.commit()
            conn.close()
            print("[+]-Record created succesfully for "+name_url)
            print("*"*70)
            table_name = (name_url, wb_name, "seo_analyser.db")
            db_table_name.append(table_name)

        except :
            print("table already exist for "+name_url)

    except:
        print("#"*70)
        print("[+]-"+name_url+" : server down or incorrect url")
        print("#"*70)
        msg = (name_url, "server down")
        db_table_name.append(msg)
# iterating through the file data and passing the url in web_data function as an argument


url_num = 1
for URL in file_data():
    name_url = "url" + str(url_num)
    if url_checker(URL):
        url_num += 1
        print("[+]-bigining to scrap the the web content.....")
        web_data(URL)
    else:
        print(5*"*")


print("[+]-process finished...")

print("#"*70)

print("database name and table name for the urls in the loaded file . eg(url, database name, table name) ")
for data in db_table_name:
    print(data)

print("#"*70)