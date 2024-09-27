import time
from datetime import datetime, timezone, timedelta
import urllib.request as ur
import urllib.error as ue
import http.client
import lxml.html as lh
import csv
from zoneinfo import ZoneInfo




import gspread
from oauth2client.service_account import ServiceAccountCredentials



url_1 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&pll=-50&plh=0&tbsl=3&tbsh=25&tnrl=2&tnrh=10&tpml=-8&tpmh=-3&cdcs=0&cdds=0&cdcd=1&cdao=0&rtall=1&rtp=1&rct=3'
url_2 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&pll=-50&plh=0&tdl=1760&tdh=9000&tbsl=3&tbsh=25&tpml=-8&tpmh=-3&cdcs=0&cdds=0&cdcd=1&cdao=0&rtall=1&rtp=1&rct=3'
url_3 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&pll=-50&plh=0&tbsl=3&tbsh=12&tpml=-8&tpmh=-3&cdcs=0&cdds=0&cdcd=1&cdao=0&rtall=1&rct=3'

file_1 = 'file_1.csv'
file_2 = 'file_2.csv'
file_3 = 'file_3.csv'

file_list = [file_1, file_2, file_3]
google_file_id = ['1BMI_IfLX2S7EA0In9pDMECajK_DQ_l4XeThx_rabYRY', '1Cu5CM6cZVHPPWcX-KobHh0b2mMuxb2bODtHBodt7eyk', '1g5uf-MGoZ_8-RRZ14M9aqhgOrkVeba1TpxYP3gpNwKs']

def get_ordinal_suffix(day):
    """Return the ordinal suffix for a given day."""
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix

def write_to_csv(file, rows):
    """Write rows to a csv file."""
    with open(file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Provider', 'EventName', 'SelectionName', 'StartTime', 'BetType'])
        if len(rows) != 0:
            for row in rows:
                writer.writerow(row)
        
def clear_csvs():
    """Clear the csv files"""
    if datetime.now(ZoneInfo('UTC')).hour == 0:
        write_to_csv('temp.csv', [])
        print('temp file cleared')
        for j in range(0, 3):
            file = file_list[j]
            write_to_csv(file, [])
            print(f'{file} cleared')
        # save_to_sheet(clear_files=True)
    with open('temp.csv', 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            row = list(reader)[0]
        except:
            row = []
        if row != []:
            date = row[3].split(' ')[0]
            print(date)
            print(datetime.now(timezone.utc).strftime('%d/%m/%Y'))
            if date != datetime.now(timezone.utc).strftime('%d/%m/%Y'):
                write_to_csv('temp.csv', [])
                print('temp file cleared')
                for j in range(0, 3):
                    file = file_list[j]
                    write_to_csv(file, [])
                    print(f'{file} cleared')
                # save_to_sheet(clear_files=True)

def save_to_sheet(file_local=None, clear_files=None):
    scope = ["https://www.googleapis.com/auth/spreadsheets"] 
    # Add your service account credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
    # Authorize the client
    client = gspread.authorize(creds)


    if clear_files:

        for j in range(0, 4):
            if j != 3:
                file_id = google_file_id[j]
            if  j == 3:
                file_id = "1HH7o2RMuPoMJpjRl9-sAzgzGzqBeMGznqP4zRaCBusY"
            # Open the Google Sheet using its ID
            sheet = client.open_by_key(file_id)

            # Select the first sheet by index (0 means the first sheet)
            worksheet = sheet.sheet1
            worksheet.clear()
            if j != 3:
                csv_file_path = file_list[j]
            if j == 3:
                csv_file_path = 'temp.csv'
            with open(csv_file_path, mode="r") as file:
                reader = csv.reader(file)
                csv_data = list(reader)

            # Update the Google Sheet with the CSV data
            worksheet.update(range_name='A1', values=csv_data)

    
    if file_local:
        if file_local == 'temp.csv':
            file_id = "1HH7o2RMuPoMJpjRl9-sAzgzGzqBeMGznqP4zRaCBusY"
        else:
            file_id = google_file_id[i]
        

            # Open the Google Sheet using its ID
        sheet = client.open_by_key(file_id)

        # Select the first sheet by index (0 means the first sheet)
        worksheet = sheet.sheet1

        # Read the CSV file
        csv_file_path = file_local
        with open(csv_file_path, mode="r") as file:
            reader = csv.reader(file)
            csv_data = list(reader)

        worksheet.clear()
        # Update the Google Sheet with the CSV data
        worksheet.update(range_name='A1', values=csv_data)



def change_to_utc(time):
    """Change local time to UTC time"""
    utc_time = str(int(time.split(':')[0]) - 1) + ':' + time.split(':')[1]
    return utc_time


def check_time(rows, file):
    """Check if time is in the future."""
    temp_row =[]
    for row in rows:
        start_time = datetime.strptime(row[3], '%d/%m/%Y %H:%M')
        start_time = start_time.replace(tzinfo=ZoneInfo('UTC'))
        print(start_time, 'start_time')
        if start_time > datetime.now(ZoneInfo('UTC')) and  start_time - datetime.now(ZoneInfo('UTC')) <= timedelta(minutes=2) or start_time < datetime.now(ZoneInfo('UTC')) :
            print(row, 'row')
            print('found')
            temp_row.append(row)
        else:
            pass
    compare_row = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            pass
        for row in reader:
            compare_row.append(row)

    print(temp_row, 'temp_row')
    print(compare_row, 'compare_row')
    if temp_row != compare_row and temp_row != []:
        print('not equal')
        write_to_csv(file, temp_row)
        # save_to_sheet(file_local=file)
        

    
    
def review_temp(temp_row):
    """Check the temp file to see if there has been new updates to the content"""
    with open('temp.csv', 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except:
            pass
        rows = list(reader)
        
        if temp_row != rows:
            write_to_csv('temp.csv', temp_row)
            # save_to_sheet(file_local='temp.csv')
            print('uploaded to temp CSV')
        else:
            print('no update made to temp CSV')


def identify_event(short_name):
    """Return the full name of an event."""
    horse_racing_courses = {
    'Aint': 'Aintree', 'Ascot': 'Ascot', 'Ayr': 'Ayr', 'Bang': 'Bangor-on-Dee', 'Bath': 'Bath',
    'Bev': 'Beverley', 'Brig': 'Brighton', 'Carl': 'Carlisle', 'Cart': 'Cartmel', 'Catt': 'Catterick',
    'ChelmC': 'Chelmsford City', 'Chelt': 'Cheltenham', 'Chep': 'Chepstow', 'Chest': 'Chester',
    'Donc': 'Doncaster', 'Epsm': 'Epsom Downs', 'Extr': 'Exeter', 'Fake': 'Fakenham', 'FfosL': 'Ffos Las',
    'Font': 'Fontwell', 'Good': 'Goodwood', 'Ham': 'Hamilton', 'Hayd': 'Haydock', 'Here': 'Hereford',
    'Hex': 'Hexham', 'Hunt': 'Huntingdon', 'Kelso': 'Kelso', 'Kemp': 'Kempton', 'Leic': 'Leicester',
    'Ling': 'Lingfield', 'Ludl': 'Ludlow', 'MrktR': 'Market Rasen', 'Muss': 'Musselburgh', 'Newb': 'Newbury',
    'Newc': 'Newcastle', 'Newm': 'Newmarket', 'Newt': 'Newton Abbot', 'Nott': 'Nottingham', 'Perth': 'Perth',
    'Plump': 'Plumpton', 'Ponte': 'Pontefract', 'Redc': 'Redcar', 'Ripon': 'Ripon', 'Salis': 'Salisbury',
    'Sand': 'Sandown', 'Sedge': 'Sedgefield', 'Sthl': 'Southwell', 'Strat': 'Stratford', 'Taun': 'Taunton',
    'Thirsk': 'Thirsk', 'Towc': 'Towchester', 'Uttox': 'Uttoxeter', 'Warw': 'Warwick', 'Weth': 'Wetherby',
    'Winc': 'Wincanton', 'Wind': 'Windsor', 'Wolv': 'Wolverhampton', 'Worc': 'Worcester', 'Yarm': 'Yarmouth',
    'York': 'York', 'Ballin': 'Ballinrobe', 'Baelle': 'Bellewstown', 'Clon': 'Clonmel', 'Cork': 'Cork',
    'Curr': 'Curragh', 'DownR': 'Down Royal', 'DownP': 'Downpatrick', 'Dund': 'Dundalk', 'Fairy': 'Fairyhouse',
    'Gal': 'Galway', 'GowP': 'Gowran Park', 'Kilb': 'Kilbeggan', 'Killar': 'Killarney', 'Layt': 'Laytown',
    'Leop': 'Leopardstown', 'Lim': 'Limerick', 'List': 'Listowel', 'Naas': 'Naas', 'Navan': 'Navan',
    'Punch': 'Punchestown', 'Rosc': 'Roscommon', 'Sligo': 'Sligo', 'Thurl': 'Thurles', 'Tipp': 'Tipperary',
    'Tram': 'Tramore', 'Wex': 'Wexford'
    }
    return horse_racing_courses.get(short_name)

while True:
    clear_csvs()
    time.sleep(10)
    try:
        html_1 = ur.urlopen(url_1).read()
        html_2 = ur.urlopen(url_2).read()
        html_3 = ur.urlopen(url_3).read()
    except ue.URLError:
        print('Error opening URL')
        time.sleep(1)
        continue
    except http.client.RemoteDisconnected:
        print('Internet connection Error')
        time.sleep(2)
        continue
    tree_1 = lh.fromstring(html_1)
    tree_2 = lh.fromstring(html_2)
    tree_3 = lh.fromstring(html_3)

    rows_1 = tree_1.xpath('//tr')    
    rows_2 = tree_2.xpath('//tr')
    rows_3 = tree_3.xpath('//tr')

    rows_list = [rows_1, rows_2, rows_3]

    provider_list = ['Josh_1', 'Josh_2', 'Josh_3']
    i = 0
    temp_row = []
    for rows in rows_list:
        print(i)
        if len(rows) == 0:
            print('No selection')
        new_row = []
        for row in rows:
            cells = row.xpath('.//td/text()')
            print(cells[0])
            date_time = f"{datetime.now(timezone.utc).strftime('%d/%m/%Y')} {change_to_utc(cells[0])}"
            day = datetime.now(timezone.utc).date().day
            month = datetime.now(timezone.utc).date().strftime('%b')
            suffix = get_ordinal_suffix(day)
            format_date = f"{day}{suffix} {month}"
            event = identify_event(cells[1])
            event_name = f"{event} {format_date}"
            time_now = datetime.now()
            new_row.append([provider_list[i], event_name or '', cells[2] or '', date_time or '', 'LAY'])
            print(date_time)
        print(new_row, end="/n/n")
        check_time(new_row, file_list[i])
        if new_row:
            temp_row.extend(new_row)
        i+=1 
    review_temp(temp_row)
