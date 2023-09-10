from bs4 import BeautifulSoup
from DataQueue import DataQueue
import re, csv, pandas
html_doc = "./webpages/webpage2.html"

ALL_DATA = {}

def formatData(data):
    headers = [ "Competition" ,
        "gender",
        "event_name",
        "event_date",
        "event_wind",
        "Round",
        "Heat"
        "No." ,
        "Athlete Name",
        "Country",
        "DOB", 
        "Time",
        "PB/SB",
        "Qualification",
        "NR",
        "Reaction Time"]
    
    has_header = False
    try:
        with open('TrackDATA.csv', "r") as file:
            has_header = csv.Sniffer().has_header(file.read(100))
    except: 
        print("facing an error with file!")

    with open('TrackDATA.csv', "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not has_header:
            writer.writeheader()
        writer.writerow(data)


def obtainAllAvailableData(row,event_name,event_id,event_date,competition_name):
    number = row.find('td').text # finds the first instance of <td> which always contains the number
    athlete_name = row.find("a",class_='mobile').text
    if '\xa0' in athlete_name:
        athlete_name = ' '.join(athlete_name.split("\xa0"))
    elif "&nbsp;" in athlete_name:
        athlete_name = ' '.join(athlete_name.split("&nbsp;"))

    drug_ban = row.find('td', class_="drugban").text
    nationality , DOB , athlete_time = row.find_all('td', class_="rc")[0].text , row.find_all('td', class_="rc")[1].text, row.find_all('td', class_="rc")[2].text.strip()
    
    try:
        personal_best_progressions = row.find_all("a",{"name\\":"Personal best progression"})
        personal_best_1 = None
        personal_best_2 = None
        if personal_best_progressions is not None and len(personal_best_progressions) > 1:
            personal_best_1 = personal_best_progressions[0].text
            personal_best_2 = personal_best_progressions[1].text
        else:
            personal_best_2 = row.find("a", {"name\\":"Seasonal best progression"}).text
    except Exception as e:
        print("exception", e)
    
    NR_data = row.find_all("td", {"align": "right"})[3].text
    other_ranking = row.select("td:last-child")[0].text
    gender = "Men" if event_id.split(".")[0] == "1" else "Women"

    data = {
        "Competition" : competition_name,
        "gender": gender,
        "event_name": event_name,
        "event_date": event_date,
        "event_wind": event_wind,
        "No." : number,
        "Athlete Name" : athlete_name,
        "Country" : nationality,
        "DOB": DOB, #date of birth
        "drugban": drug_ban,
        "Time": athlete_time,
        "Personal_best_1" : personal_best_1,
        "Personal_best_2" : personal_best_2,
        "NR": NR_data,
        "other_ranking": other_ranking
    }

    return data
#use a dictionary to contain event, heat, and add list of all available data for individual heat


"""
only concerned with: 100m, 100m hurdles, 110m hurdles, 200m, 400m, 400m hurdles
1) if the data is consistent then loop through different event id numbers.
2) clean up the code a little bit.
"""



competitions = [
# "2010 Commonwealth games Delhi",
# "2012 London olympics",
# "2013 Asian championship",
# "2014 Asian games",
# "2014 Commonwealth games Glasgow",
# "2015 Asian championship",
# "2016 Rio Olympics",
# "2017 Asian championship",
# "2018 Asian games",
# "2018 Commonwealth games",
# "2019 Asian championships",
# "2021 Tokyo Olympics",
# "2022 commonwealth games",
"2023 World Athletics Championships Budapest"
]

for comp in competitions:
    html_doc = "./webpages/" + f"{comp}.html" 
    print(f"Command: Obtaining Data for {comp}")
    with open(html_doc, 'r', encoding="utf-8") as html:
        event_data = {}
        event_ids = ["1.500.", "2.500.", "1.550.","1.500.000000.", "2.500.000000.", "1.550.000000."] #"1.500.", "2.500.", "1.550.", "1.500.000000.", "2.500.000000.", "1.550.000000." 000000.
        athlete_data = DataQueue() # queue to keep track of data
        soup = BeautifulSoup(html,'html.parser')
        

        for event_id in event_ids:
            event_tag = soup.find('td', {"class": 'event', "id" : event_id})
            if not event_tag:
                print(f"event_tag for {event_id} not found")
                continue

            event_date = event_tag.parent.find_all('td', class_="date")[0].text
        
        
            event_wind=  event_tag.parent.find_all('td', class_="date")[1].text
            event_name = event_tag.b.text
            # event_data = {"event_name":""}
            # athlete_data.enqueue()
            # print("DATA SET ---->", {"event_date":event_date, "event_wind": event_wind, "event_name": event_name})
            row = event_tag.parent.find_next_sibling('tr') # gives the next <tr> sibling 
            
            # initial default values. These values are changed accordingly

            while True:
                if row.find("td", {"class": 'event', "id" : re.compile(r"\d\.\d\d?\d\.")}):
                    # print("next event")
                    break
                elif row.find('td', class_="round"):
                    # event_round refers to finals, semifinals, heat
                    data_found = row.find_all('td')
                    event_round = data_found[1].b.text
                    event_round_date = " ".join(data_found[2].text.split('&nbsp;'))
                    if "\xa0" in event_round_date:
                        event_round_date = " ".join(event_round_date.split("\xa0"))
                    event_round_data = {"round":event_round,"round_date": event_round_date}
                    
                    ROUND = event_round
                    event_date = event_round_date

                    # print(f"event_round: {event_round}, event_round_date: {event_round_date}")


                    row = row.find_next_sibling('tr')
                    #pass
                elif row.find('td', class_="date"):
                    try:
                        data_found = row.find_all('td', class_='date')
                        if data_found[2].text:
                            # heat referes to sub events such as heat1, heat 2, finals(default)
                            heat_round = data_found[1].b.text
                            heat_wind = data_found[2].text
                            heat_round_data = {"heat":heat_round,"heat_wind": heat_wind}

                            event_wind = heat_wind # sets the new wind according to the heat
                            HEAT = heat_round
                            # print(f"heat_round: {heat_round}, heat_wind: {heat_wind}")
                            
                            row = row.find_next_sibling('tr')
                        else:
                            heat_round = data_found[1].b.text
                            heat_round_data = {"heat":heat_round,"heat_wind": None}
                            
                            event_wind = heat_wind # sets the new wind according to the heat
                            HEAT = heat_round
                            
                            # print(f"subEvent_round: {heat_round}, subEvent_wind: None")

                            row = row.find_next_sibling('tr')

                    except:
                        print("error")
                        print('data that is causing error ----->', row.find_all('td', class_='date'))
                        print('breaking')
                        break
        
                    # print(f"subEvent_round: {subEvent_round}, subEvent_wind: {subEvent_wind}")
                    # athlete_data.enqueue(event_round_date)
                    # row = row.find_next_sibling('tr')
                else:
                    athlete_data.enqueue(obtainAllAvailableData(row, event_date=event_date, event_id=event_id,event_name=event_name, competition_name=comp))
                    # posibility that the event_wind will override the heat_wind

                    # if row.find_next_sibling('tr').find("td", {"colspan":7}):
                    #     row = row.find_next_sibling('tr')
                    row = row.find_next_sibling('tr')
        
        

        print("Command: Formatting to CSV")
        headers = [ "Competition",
            "gender",
            "event_name",
            "event_date",
            "event_wind",
            "No.",
            "Athlete Name", 
            "Country",
            "DOB",
            "drugban",
            "Time",
            "Personal_best_1",
            "Personal_best_2",
            "NR",
            "other_ranking"]
        
        has_header = False
        try:
            with open('./data/MultiEventsDATA.csv', "r") as file:
                has_header = csv.Sniffer().has_header(file.read(100))
        except: 
            print("facing an error with file!")

        with open('./data/MultiEventsDATA.csv', "a", newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not has_header:
                writer.writeheader()
            while athlete_data.is_empty() != True:
                data = athlete_data.dequeue()
                writer.writerow(data)
        
        print("Command: Done")
        

        