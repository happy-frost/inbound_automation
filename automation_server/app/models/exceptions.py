class Mismatch(Exception):
    def __init__(self,message="there is a mismatch"):
        super().__init__(f"{message}")

class Document(Exception):
    def __init__(self,message="there is an error with the document"):
        super().__init__(f"{message}")