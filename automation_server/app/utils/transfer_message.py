import pandas as pd
import re
import datetime

class Transfer:
    def __init__(self, time, from_loc, to_loc, tour, driver, vehicle_number, contact):
        self.time=time
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.tour = tour
        self.driver = driver
        self.vehicle_number = vehicle_number
        self.contact = contact

class Customer_Tranfer:
    def __init__(self,guest_name,date):
        self.guest_name = guest_name
        self.date = date
        self.transfers = []

    def add_transfer(self,transfer:Transfer):
        self.transfers.append(transfer)

    def output_message(self):
        out = []
        for t in self.transfers:
            if t.vehicle_number:
                out.append(f'{t.time}\nFrom: {t.from_loc.capitalize()}\nTo: {t.to_loc.capitalize()}\nType: {t.tour}\nContact Person: {t.driver}\nVehicle Number: {t.vehicle_number}\nContact: {t.contact}\n\n')        
            else:
                out.append(f'{t.time}\nFrom: {t.from_loc.capitalize()}\nTo: {t.to_loc.capitalize()}\nType: {t.tour}\nContact Person: {t.driver}\nContact: {t.contact}\n\n')
        return ''.join(out)

    def additional_message(self,special_location: list[str]):
        match = {t.from_loc for t in self.transfers if t.from_loc in special_location}
        if match:
            return match


def get_customer_transfers(file_path):
    customer_transfers = []
    try:
        df = pd.read_excel(file_path)
        df.dropna()
        for _, row in df.iterrows():
            if pd.isna(row.Date):
                continue
            date = row.Date.to_pydatetime()
            time = datetime.time.strftime(row.Time,"%I:%M %p")
            
            details = row.DETAILS.split(" ")
            driver = details[0]
            # Check that full vehicle number (contain both alpha and numeric) otherwise combine with next item on list
            if re.search('^[a-zA-Z]*\\d',details[1]):
                vehicle_number = details[1]  
            elif re.search('^[a-zA-Z]*\\d', ''.join(details[1:3])):
                vehicle_number = ''.join(details[1:3])
            else:
                vehicle_number = ''
            # Check that last item has country code otherwise combine with second last item)
            contact = details[-1] if details[-1].startswith("+65") else "".join(details[-2:])

            if driver.strip().lower() == "roselin":
                driver = "Irvinder"
                contact = "+6591808379"

            match = {c.guest_name: c for c in customer_transfers if c.guest_name == row.Guest}
            if len(match) == 0:
                ct = Customer_Tranfer(row.Guest,date)
                customer_transfers.append(ct)
            else:
                ct = match[row.Guest]
            
            ct.add_transfer(Transfer(time,row.From.lower(),row.To.lower(),row.Tour,driver,vehicle_number,contact))
        
        return customer_transfers
    except Exception as e:
        print(e)
        return None