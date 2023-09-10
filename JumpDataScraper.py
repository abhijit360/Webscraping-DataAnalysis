from bs4 import BeautifulSoup
from DataQueue import DataQueue
import re, csv, pandas


print("Command: Obtaining Data")

def obtainAllAvailableData(athlete_row, athlete_data_row, event_date, event_id,event_name, competition_name, round):
    number = athlete_row.find("td").text
    athlete_name = athlete_row.find("a" , class_="mobile").text
    drug_ban = athlete_row.find("td", class_="drugban").text

    class_rc_tds = athlete_row.find_all("td", class_="rc")
    nationality, DOB, furthest_jump = class_rc_tds[0].text, class_rc_tds[1].text, class_rc_tds[2].text.strip()

    decimal_data = athlete_row.find_all("td", {"align":"right"})[2].text
    NR_data =  athlete_row.find_all("td", {"align":"right"})[3].text

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
        if furthest_jump != "DNS" and furthest_jump !="NM":
            all_jump_data = athlete_data_row.find("td", {"colspan": "7"}).text
        else:
            all_jump_data ="DNS"
    except Exception as e:
        all_jump_data = "DNE"

    
   
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
        "furthest_jump": furthest_jump,
        "decimal_data": decimal_data,
        "NR_data" : NR_data,
        "all_jumps": all_jump_data,
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

    print(f"--> Command: Obtaining Data for {comp} <--")
    with open(html_doc, 'r', encoding="utf-8") as html:
        event_data = {}
        event_ids = ["1.330.","2.330.", "1.340.", "2.340.", "1.310.", "2.310.","1.330.000000.", "2.330.000000.", "1.340.000000.", "2.340.000000.", "1.310.000000.", "2.310.000000."] 
        #"1.330.", "2.330.", "1.340.", "2.340.", "1.310.", "2.310."
        #"1.330.000000.", "2.330.000000.", "1.340.000000.", "2.340.000000.", "1.310.000000.", "2.310.000000."
        #000000.
        athlete_data = DataQueue() # queue to keep track of data
        soup = BeautifulSoup(html,'html.parser')


        for event_id in event_ids:
            event_tag = soup.find('td', {"class": 'event', "id" : event_id})

            if not event_tag:
                print(f"event_tag for id: {event_id} not found")
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
                else:
                    data = obtainAllAvailableData(athlete_row=row, athlete_data_row= row.find_next_sibling('tr'), event_date=event_date, event_id=event_id,event_name=event_name, competition_name=comp, round=ROUND)

                    athlete_data.enqueue(data)

                    furthest_jump = row.find_all("td", class_="rc")[2].text.strip()
                    if furthest_jump == "DNS":
                        row = row.find_next_sibling('tr') # next athlete row
                    else:
                        row = row.find_next_sibling('tr') # skips the athlete_data_row
                        row = row.find_next_sibling('tr') # next athlete row
        
                
        

        print("Command: Formatting to CSV")
        headers = ["competition",
            "event",
            "date",
            "round",
            "number",
            "name",
            "drug ban",
            "nationality",
            "DOB",
            "furthest_jump",
            "decimal_data",
            "NR_data",
            "all_jumps",
            "Personal_best_progression",
            "Seaonal_best_progression",
            "qualification",
            "misc_data",
            "Gender"]
        
        has_header = False
        try:
            with open('./data/JumpDATA.csv', "r+") as file:
                has_header = csv.Sniffer().has_header(file.read(100))
        except Exception as e: 
            print("facing an error with file!", e)

        with open('./data/JumpDATA.csv', "a", newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not has_header:
                writer.writeheader()
            while athlete_data.is_empty() != True:
                data = athlete_data.dequeue()
                writer.writerow(data)
        
        print("Command: Done")
       
