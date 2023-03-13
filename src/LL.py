import src.PreSAT  as PreSAT
import src.PostSAT as PostSAT
from src.utils import *

class LogicLocking:
    def __init__(self,obj) -> None:
        self.module=obj.top_module
        self.PreSAT=PreSAT.PreSAT(self.module)
        self.PostSAT=PostSAT.PostSAT(self.module)
        print("LogicLocking obj created")
    


    
