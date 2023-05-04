

class MDA_Database:
    """
    This is merely a storage format that can associate  Tuple->EC  and  EC->Tuples.
    It also contains some usefull Functions for manipulating ECs or printing the DB.

    Contrary to what the Function-Parameters say, EC-IDs can also be Integers instead of Strings - it will still work!
    """
    """
    Tuples_Table
    A Table that maps each tuple to an EC-ID.
    (can be optimised by making it a sorted dict Firstletter->(SecondLetter, EC-ID))
    For now it's a nested Dict:
                Dict[Firstletter] -> ( Dict[SecondLetter] -> EC-ID )
    """
    """
    EC_Table
    A Table that gives you for each EC-ID a list of Tuples that have been assigned to it.
    For now:
                Dict[EC-ID]  ->  List(*Tuple of FirstLetter+LastLetter*)
    """


    # DONE, Works---
    def __init__(self):
        self.Tuples_Table = {}  # a Dictionary
        self.EC_Table = {}      # a Dictionary too

    # DONE, Works---
    def set_Tuple_EC(self, Tuple: tuple, EC_id: str):
        """
        Sets the given Tuples EC. (in both views btw)
        Creates a new Tuple-Entry and/or EC-Entry if needed.
        (Doubles impossible cuz the Tuple-view only allows for singular assignment.)
        """

        firstletter = Tuple[0]
        secondletter = Tuple[1]

        if firstletter not in self.Tuples_Table.keys():  # if toplevel Dict doesn't even contain the first letter:
            self.Tuples_Table[firstletter] = {}          # create an empty Dictionary

        firstletter_dict = self.Tuples_Table[firstletter]
        if secondletter in firstletter_dict.keys():     # if the Tuple already exists, do the following first:
            old_EC_id = firstletter_dict[secondletter]
            self.__remove_Tuple_from_EC_in_ECTable(Tuple, old_EC_id)

        firstletter_dict[secondletter] = EC_id              # assign ECs ID to the Tuple
        self.__add_Tuple_to_EC_in_ECTable(Tuple, EC_id)     # insert the Tuple into the ECs Tuple-List

    # DONE, Works---
    def get_EC_of_Tuple(self, Tuple: tuple) -> str:
        """
        Returns the EC-ID of the EC that the Tuple was assigned to.
        Returns NULL if not registered in DB at all.
        """
        firstletter = Tuple[0]
        secondletter = Tuple[1]
        if self.check_if_Tuple_exists(Tuple) == False:
            return None
        return self.Tuples_Table[firstletter][secondletter]

    # DONE, Works---
    def get_Tuples_of_EC(self, EC_id: str) -> list:
        """
        Returns a list of all Tuples that are assigned to the given EC.
        Returns NULL if not registered in DB at all.
        """
        if self.check_if_EC_exists(EC_id) == False:
            return None
        return self.EC_Table[EC_id]

    # DONE, Works---
    def get_representative_of_EC(self, EC_id: str) -> tuple:
        """
        Returns a ""random"" Tuple from the EC.
        Returns NULL if not registered in DB at all.
        """
        if self.check_if_EC_exists(EC_id) == False:
            return None
        return self.EC_Table[EC_id][0]

    # DONE, Works---
    def check_if_Tuple_exists(self, Tuple: tuple) -> bool:
        """
        Returns true if the given Tuple is assigned to any EC in the Database.
        """
        firstletter = Tuple[0]
        secondletter = Tuple[1]
        # TODO might improve runtime if i just ry-except for indexError when trying dict[letter]
        if firstletter in self.Tuples_Table.keys():
            if secondletter in self.Tuples_Table[firstletter].keys():
                return True
        return False

    # DONE, Works---
    def check_if_Tuple_in_EC(self, Tuple: tuple, EC_id: str) -> bool:
        """
        Returns true if there is this exact Tuple in the given EC.
        """
        if self.check_if_EC_exists(EC_id) == False:
            return False
        TupleList = self.EC_Table[EC_id]
        if Tuple in TupleList:
            return True
        return False

    # DONE, Works---
    def merge_ECs(self, EC_from: str, EC_to: str):
        """
        Merges EC A into B.
        A.K.A:   all Tuples from A get mapped to B,  and A gets deleted.
        (doesn't check for conflicts.)
        """
        if EC_from not in self.EC_Table.keys():
            return
        if EC_to not in self.EC_Table.keys():
            return

        # this needs to be a copy, otherwise the element-removal might somehow fuck the for-loop up,
        # causing some Tuples to not be moved.
        Tuplelist = self.EC_Table[EC_from].copy()

        for Tuple in Tuplelist:     # move all Tuples to the new EC, removing them from the old EC
            self.set_Tuple_EC(Tuple, EC_to)

        self.__delete_empty_EC_in_ECTable(EC_from)   # delete the now empty old EC.

    # DONE, Works---
    def get_global_TupleList(self) -> list:
        """
        Returns a list, containing ALL Tuples of the Database.
        """
        result_List = []
        for EC_id in self.EC_Table:
            ECs_Tuples = self.get_Tuples_of_EC(EC_id).copy()
            result_List.extend(ECs_Tuples)
        return result_List

    # DONE, Works(probably, can't remember)---
    def get_TupleMapping_flattened(self) -> dict:
        """
        Returns the TupleTable, but flattens the nested dictionaty [str->[str->EC]] into a Tuple-Dictionary  [Tuple->EC]
        """
        result_dict = {}
        for EC_id in self.EC_Table:
            ECs_Tuples = self.get_Tuples_of_EC(EC_id).copy()
            for Tuple in ECs_Tuples:
                result_dict[Tuple] = EC_id
        return result_dict

    # DONE, Works---
    def create_empty_EC(self, EC_id: str):
        """
        Creates an empty Entry for the given EC in the Database.
        """
        if EC_id in self.EC_Table:  # (do nothing if already exists.)
            return
        self.EC_Table[EC_id] = []

    # DONE, Works---
    def check_if_EC_exists(self, EC_id: str) -> bool:
        return EC_id in self.EC_Table.keys()

    # DONE, Works---
    def __remove_Tuple_from_EC_in_ECTable(self, Tuple: tuple, EC_id: str):
        """
        (NOT for outsider use, cuz it desyncs the two DB-views)
        does nothing if the EC doesn't exist or didn't contain that Tuple.
        """
        if self.check_if_EC_exists(EC_id) == False:
            return

        try:
            self.EC_Table[EC_id].remove(Tuple)
        except ValueError:  # (just ignore any possible ValueErrors)
            return
        return

    # DONE, Works---
    def __add_Tuple_to_EC_in_ECTable(self, Tuple: tuple, EC_id: str):
        """
        (NOT for outsider use, cuz it desyncs the two DB-views)
        ((Creates a new EC if needed))
        """
        if self.check_if_EC_exists(EC_id) == False:
            self.create_empty_EC(EC_id)

        if Tuple not in self.EC_Table[EC_id]:
            self.EC_Table[EC_id].append(Tuple)

    # DONE, Works---
    def __delete_empty_EC_in_ECTable(self, EC_id: str):
        """
        (NOT for outsider use, cuz it desyncs the two DB-views)
        Simply removes the given EC from the EC Table.
        Can also be used on non-empty ECs, but that isn't good manners...
        """
        self.EC_Table.pop(EC_id)


    # -----------------------------------
    # --------- PRINT-Functions ---------
    # -----------------------------------
    # DONE, Works---
    def print_Tuples_Table(self):
        for firstletter in self.Tuples_Table:
            for secondletter in self.Tuples_Table[firstletter]:
                EC_id = self.Tuples_Table[firstletter][secondletter]
                output = firstletter + secondletter + " -> " + EC_id.__str__()
                print(output)

    # DONE, Works---
    def print_EC_Table(self):
        for EC_id in self.EC_Table:
            TupleList = self.EC_Table[EC_id]
            output = f"[{EC_id}] : " + self.niceformat_of_TupleList(TupleList)
            print(output)

    # DONE, Works---
    def print_EC_Table_detailed(self):
        """
        Basically  print_EC_Table(), but it adds the total size of each EC after each EC.
        """
        for EC_id in self.EC_Table:
            TupleList = self.EC_Table[EC_id]
            EC_size = TupleList.__len__()
            output = f"[{EC_id}] : " + self.niceformat_of_TupleList(TupleList) + " \t" +EC_size.__str__()
            print(output)

    # DONE, Works---
    @staticmethod
    def niceformat_of_TupleList(TupleList: list) -> str:
        """
        Used for the above printing-functions.
        """
        output = "("
        first = True
        for Tuple in TupleList:
            if first:
                first = False
            else:
                output = output + ","
            output = output + Tuple[0] + Tuple[1]
        output = output + ")"
        return output

