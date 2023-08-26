#Each excel tab will have a different event
import pandas
csv_files = ["TrackData"]
for csv_file in csv_files:
    data_frame = pandas.read_csv("./data/"+f"{csv_file}.csv")
    # print("columns--->", data_frame.columns)
    # print("-->___>")
    event_names = data_frame["event_name"].unique()
    with pandas.ExcelWriter("./data/TrackExcel.xlsx") as writer:
        for event in event_names:
            print(f"working with {event}")
            event_data = data_frame[data_frame["event_name"] == event]
            data_frame.to_excel(writer, sheet_name=event, index=False)