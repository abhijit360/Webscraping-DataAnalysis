from bs4 import BeautifulSoup
from DataQueue import DataQueue
import re, csv, pandas
html_doc = "./webpages/webpage2.html"

print("Command: Obtaining Data")

def obtainAllAvailableData(athlete_row, athlete_data_row, event_date, event_id,event_name, competition_name, round):
    number = athlete_row.find("td").text
    try:
        athlete_name = athlete_row.find("a" , class_="mobile").text
    except Exception as e:
        print("exception --->", e)
        print(athlete_row.prettify())
    drug_ban = athlete_row.find("td", class_="drugban").text

    class_rc_tds = athlete_row.find_all("td", class_="rc")
    nationality, DOB, furthest_throw = class_rc_tds[0].text, class_rc_tds[1].text, class_rc_tds[2].text.strip()

    AR_data = athlete_row.find_all("td", {"align":"right"})[3].text

    try:
        personal_best_progressions = athlete_row.find_all("a",{"name\\":"Personal best progression"})
        personal_best_1 = None
        personal_best_2 = None
        if personal_best_progressions is not None and len(personal_best_progressions) > 1:
            personal_best_1 = personal_best_progressions[0].text
            personal_best_2 = personal_best_progressions[1].text
        else:
            personal_best_2 = athlete_row.find("a", {"name\\":"Seasonal best progression"}).text
    except Exception as e:
        print("exception", e)
       

    qualification = athlete_row.select("td:nth-last-child(2)")[0].text.upper()
    Misc_data = row.select("td:nth-last-child(1)")[0].text
    try:
        if furthest_throw != "DNS":
            all_throw_data = athlete_data_row.find("td", {"colspan": "7"}).text
        else:
            all_throw_data ="DNS"
    except Exception as e:
        print("exception -->",e)
        all_throw_data = "DNS"

    gender = "Men" if event_id.split(".")[0] == "1" else "Women"

    return {
        "competition": competition_name,
        "event": event_name,
        "date": event_date,
        "round": round,
        "number":number,
        "name": athlete_name,
        "drug ban": drug_ban,
        "nationality": nationality,
        "DOB": DOB,
        "furthest_throw": furthest_throw,
        "all_throws": all_throw_data,
        "AR_data": AR_data,
        "Personal_best_progression": personal_best_1,
        "Seaonal_best_progression": personal_best_2,
        "qualification": qualification,
        "misc_data":Misc_data,
        "Gender": gender,
    }

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
        event_ids = ["1.350.", "1.360." , "1.380." , "1.390." , "2.350." , "2.360." ,"2.380.", "2.390.","1.350.000000.", "1.360.000000." , "1.380.000000." , "1.390.000000." , "2.350.000000." , "2.360.000000." ,"2.380.000000.", "2.390.000000."]
         #"1.350.", "1.360." , "1.380." , "1.390." , "2.350." , "2.360." ,"2.380.", "2.390."
         #"1.350.000000.", "1.360.000000." , "1.380.000000." , "1.390.000000." , "2.350.000000." , "2.360.000000." ,"2.380.000000.", "2.390.000000."
        athlete_data = DataQueue() # queue to keep track of data
        soup = BeautifulSoup(html,'html.parser')
        

        for event_id in event_ids:
            event_tag = soup.find('td', {"class": 'event', "id" : event_id})
            if not event_tag:
                print(f"Event for id: {event_id} not found")
                continue
            event_name = event_tag.b.text
            event_date = event_tag.parent.find("td", class_="date").text

            print(f"event_name: {event_name}, event_date: {event_date}")
        
        
            row = event_tag.parent.find_next_sibling('tr') # gives the next <tr> sibling 
            
            ROUND = "Finals"  
            
            while True:
                if row.find("td", {"class": 'event', "id" : re.compile(r"\d\.\d\d?\d\.")}):
                    # print("next event")
                    break
                elif row.find('td', class_="round"):
                    # event_round refers to finals, semifinals, heat
                    data_found = row.find_all('td')
                    event_round = data_found[1].b.text
                    event_round_date = data_found[2].text
                    # if "\xa0" in event_round_date:
                    #     event_round_date = " ".join(event_round_date.split("\xa0"))
                    # event_round_data = {"round":event_round,"round_date": event_round_date}
                    
                    ROUND = event_round
                    event_date = event_round_date
                    print(f"round: {ROUND}, event_date:{event_round_date}")
                    # print(f"event_round: {event_round}, event_round_date: {event_round_date}")


                    row = row.find_next_sibling('tr')
                    #pass
                elif row.find("td", class_="date"):
                    ROUND = row.find_all("td", class_="date")[1].text
                    row = row.find_next_sibling('tr')
                else:
                    data = obtainAllAvailableData(athlete_row=row, athlete_data_row= row.find_next_sibling('tr'), event_date=event_date, event_id=event_id,event_name=event_name, competition_name=comp, round=ROUND)

                    athlete_data.enqueue(data)

                
                    row = row.find_next_sibling('tr') # skips the athlete_data_row
                    row = row.find_next_sibling('tr') # next athlete row
        
        

        print("Command: Formatting to CSV")
        headers = [ "competition",
            "event",
            "date",
            "round",
            "heat",
            "number",
            "name",
            "drug ban",
            "nationality",
            "DOB",
            "furthest_throw",
            "all_throws",
            "AR_data",
            "Personal_best_progression",
            "Seaonal_best_progression",
            "qualification",
            "misc_data",
            "Gender"]
        
        has_header = False
        try:
            with open('./data/ThrowsDATA.csv', "r+") as file:
                has_header = csv.Sniffer().has_header(file.read(100))
        except Exception as e: 
            print("facing an error with file!", e)

        with open('./data/ThrowsDATA.csv', "a", newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not has_header:
                writer.writeheader()
            while athlete_data.is_empty() != True:
                data = athlete_data.dequeue()
                writer.writerow(data)
        
        print("Command: Done")
        print("command: cleaning Data")

        