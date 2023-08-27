#Each excel tab will have a different event
import pandas
csv_files = ["TrackData", "ThrowsData"]
for csv_file in csv_files:
    data_frame = pandas.read_csv("./data/"+f"{csv_file}.csv")
    if "event_name" in data_frame.columns:
        event_names = data_frame["event_name"].unique()
        with pandas.ExcelWriter("./data/"+ f"{csv_file}.xlsx") as writer:
            for event in event_names:
                print(f"working with {event}")
                event_data = data_frame[data_frame["event_name"] == event]
                event_data.to_excel(writer, sheet_name=event, index=False)
    elif "event" in data_frame.columns:
        event_names = data_frame["event"].unique()
        with pandas.ExcelWriter("./data/"+ f"{csv_file}.xlsx") as writer:
            for event in event_names:
                print(f"working with {event}")
                event_data = data_frame[data_frame["event"] == event]
                event_data.to_excel(writer, sheet_name=event, index=False)
            