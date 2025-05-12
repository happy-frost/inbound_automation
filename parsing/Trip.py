import datetime
import copy
from . import exceptions
from docx import Document

class Ticket:
    def __init__(self,name: str,date:str):
        self.name = name
        self.date = datetime.datetime.strptime(date,"%d %b %y")
        self.bought = False


class Trip:
    def __init__(self,file_path):
        self.guest_name = ""
        self.start_date = None
        self.end_date = None
        self.adults = 0
        self.children = 0
        self.children_above_six = 0
        self.children_below_six = 0
        self.attraction_tickets = []
        
        document = Document(file_path)
        parsing_guest = False
        parsing_ticket = False

        for paragraph in document.paragraphs:
            if paragraph.text.startswith("Guest name"):
                guest = paragraph.text.split("\t")[1].split(" X ")
                self.guest_name = guest[0]
                guest_num = guest[1] # get the guest num from guest name
                parsing_guest = True
                continue

            if parsing_guest:
                if paragraph.text.__contains__("+"):
                    guest_num += paragraph.text.strip("\t")
                else:
                    parsing_guest = False
            
            if paragraph.text.startswith("Tickets"):
                guest_num_ticket = paragraph.text.split(" for ")[1] # get the guest num from tickets header
                parsing_ticket = True
                continue

            if parsing_ticket:
                if paragraph.text == "":
                    parsing_ticket = False
                    continue
                day, tickets_for_the_day = paragraph.text.strip(".").split(":")
                tickets_for_the_day = tickets_for_the_day.strip().split(", ")
                for item in tickets_for_the_day:
                    self.attraction_tickets.append(Ticket(item,day))
        
        if guest_num != guest_num_ticket:
            raise exceptions.Mismatch("there is a mismatch in the number of guest")

        guests = guest_num.split("+")
        for category in guests:
            if category.__contains__("adults"):
                self.adults = int(category.split(" ")[0])
            
            if category.__contains__("child"):
                self.children = int(category.strip().split(" ")[0])
                children_age_str = category.strip().split("(")[-1].strip("years)").split(" / ")
                children_age = list(map(lambda x: int(x.strip()), children_age_str))

                for age in children_age:
                    if age <= 6:
                        self.children_below_six += 1
                    else:
                        self.children_above_six += 1
    
    def tickets_to_buy(self):
        tickets_to_buy = copy.deepcopy(self.attraction_tickets)
        