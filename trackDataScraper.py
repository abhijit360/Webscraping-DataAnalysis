from bs4 import BeautifulSoup
from DataQueue import DataQueue
import re, csv, pandas


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


def obtainAllAvailableData(row,event_name,event_id,event_date,event_wind,competition_name, round, heat):
    number = row.find('td').text # finds the first instance of <td> which always contains the number
    athlete_name = row.find("a",class_='mobile').text
    if '\xa0' in athlete_name:
        athlete_name = ' '.join(athlete_name.split("\xa0"))
    elif "&nbsp;" in athlete_name:
        athlete_name = ' '.join(athlete_name.split("&nbsp;"))

    drug_ban = row.find('td', class_="drugban").text
    nationality , DOB , athlete_time = row.find_all('td', class_="rc")[0].text , row.find_all('td', class_="rc")[1].text, row.find_all('td', class_="rc")[2].text.strip()
    
    # date = row.find('td', class_='desktop rc').text
    # record_title , record_value = row.find_all('a', attrs={"name": "Personal best progression"})[0].text , row.find_all('a', attrs={"name": "Personal best progression"})[1].text
    # record_data = row.find_all('a', attrs={"name": "Personal best progression"})
    
    record_data = []
    for child in row.children:
        data = child.find('a', attrs={"name\\": "Personal best progression"})
        if data:
            record_data.append(data.text)
    qualification_element = row.select("td:nth-last-child(2)")
    qualification = qualification_element[0].text if qualification_element else None

    td_elements = row.find_all("td", {"align":"right"})
  
    # Apply .select() on each <td> element to get the last child
    additional_record_information = row.find_all("td",  {"align":"right"})[3].text

    reaction_time = row.select("td:last-child")[0].text.strip()

    gender = "Men" if event_id.split(".")[0] == "1" else "Women"

    data = {
        "Competition" : competition_name,
        "gender": gender,
        "event_name": event_name,
        "event_date": event_date,
        "event_wind": event_wind,
        "Round": round,
        "Heat": heat,
        "No." : number,
        "Athlete Name" : athlete_name,
        "Country" : nationality,
        "DOB": DOB, #date of birth
        "Drugban": drug_ban,
        "Time": athlete_time,
        "PB/SB" : record_data,
        "Qualification": qualification.upper(),
        "NR": additional_record_information,
        "Reaction Time": reaction_time
    }

    return data
#use a dictionary to contain event, heat, and add list of all available data for individual heat


"""
only concerned with: 100m, 100m hurdles, 110m hurdles, 200m, 400m, 400m hurdles
1) if the data is consistent then loop through different event id numbers.
2) clean up the code a little bit.
"""



competitions = ["2010 Commonwealth games Delhi",
"2012 London olympics",
"2013 Asian championship",
"2014 Asian games",
"2014 Commonwealth games Glasgow",
"2015 Asian championship",
"2016 Rio Olympics",
"2017 Asian championship",
"2018 Asian games",
"2018 Commonwealth games",
"2019 Asian championships",
"2021 Tokyo Olympics",
"2022 commonwealth games"]

for comp in competitions:
    html_doc = "./webpages/" + f"{comp}.html" 

    print(f"Command: Obtaining Data for {comp}")
    with open(html_doc, 'r', encoding="utf-8") as html:
        event_data = {}
        event_ids = ["1.40.","1.50.","1.70.","1.270.","1.300.",'2.40.','2.50.','2.70.','2.260.','2.300.',
                     "1.40.000000.","1.50.000000.","1.70.000000.","1.270.000000.","1.300.000000.",'2.40.000000.','2.50.000000.',
                     '2.70.000000.','2.260.000000.','2.300.000000.'] 
        #"1.50.","1.70.","1.270.","1.300.",'2.40.','2.50.','2.70.','2.260.','2.300.'
        #"1.40.000000.","1.50.000000.","1.70.000000.","1.270.000000.","1.300.000000.",'2.40.000000.','2.50.000000.','2.70.000000.','2.260.000000.','2.300.000000.'
        athlete_data = DataQueue() # queue to keep track of data
        soup = BeautifulSoup(html,'html.parser')
        

        for event_id in event_ids:
            event_tag = soup.find('td', {"class": 'event', "id" : event_id})
            if not event_tag:
                print(f"Event tag for {event_id} not found")
                continue

            event_date = " ".join(event_tag.parent.find_all('td', class_="date")[0].text.split("\xa0"))
        
        
            event_wind=  event_tag.parent.find_all('td', class_="date")[1].text
            event_name = event_tag.b.text
            # event_data = {"event_name":""}
            # athlete_data.enqueue()
            # print("DATA SET ---->", {"event_date":event_date, "event_wind": event_wind, "event_name": event_name})
            row = event_tag.parent.find_next_sibling('tr') # gives the next <tr> sibling 
            
            ROUND = "Finals" 
            HEAT = "Finals"  
            # initial default values. These values are changed accordingly

            while True:
                if row.find("td", {"class": 'event', "id" : re.compile(r"\d\.\d\d?\d\.(\d*)?")}):
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
                    athlete_data.enqueue(obtainAllAvailableData(row, event_date=event_date, event_id=event_id,event_name=event_name, event_wind=event_wind, competition_name=comp, round=ROUND,heat=HEAT))
                    # posibility that the event_wind will override the heat_wind

                    # if row.find_next_sibling('tr').find("td", {"colspan":7}):
                    #     row = row.find_next_sibling('tr')
                    row = row.find_next_sibling('tr')
        
        

        print("Command: Formatting to CSV")
        headers = [ "Competition" ,
            "gender",
            "event_name",
            "event_date",
            "event_wind",
            "Round",
            "Heat",
            "No." ,
            "Athlete Name",
            "Country",
            "DOB", 
            "Drugban",
            "Time",
            "PB/SB",
            "Qualification",
            "NR",
            "Reaction Time"]
        
        has_header = False
        try:
            with open('./data/TrackDATA.csv', "r") as file:
                has_header = csv.Sniffer().has_header(file.read(100))
        except: 
            print("facing an error with file!")

        with open('./data/TrackDATA.csv', "a", newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not has_header:
                writer.writeheader()
            while athlete_data.is_empty() != True:
                data = athlete_data.dequeue()
                writer.writerow(data)
        
        print("Command: Done")
        
        
        