
from theBackrooms.MDA_Database import MDA_Database

SPACING_letter = "°"

class CypherAnalyzer:
    """
    This class is responsible for drawing conclusions about ECs from the provided Isomorphs
    and properly inserting those conclusions into the DB.
    """

    # DONE, Works---
    def __init__(self):
        self.DB = MDA_Database()
        self.next_EC_id = 1

    # DONE, Works---
    def ingest_new_Tuple_Equality(self, Tuple_A: tuple, Tuple_B: tuple):
        """
         [A]=[B]  and all the conclusions that follow from it get computed and
         inserted into the DB automatically.
         (Including EC-Rotation, and possible EC-Merging and all new rotations that come from the merging.)
        """
        DB = self.DB

        # -------- Initial Merge --------
        self.__shallow_new_Tuple_Equality(Tuple_A, Tuple_B)
        result_ECs_id = DB.get_EC_of_Tuple(Tuple_A)
        # at this point, A and B are in the same ECs and got conflict-checked, but no rotations generated yet.

        # -------- Working off the T0DO-List --------
        todolist = set()    # using a set for easy duplicate-prevention
        todolist.add(result_ECs_id)  # start off with only that new EC in the T0DO-List

        while True:
            curr_EC = todolist.pop()    # remove the currently worked EC from T0DO-List
            if DB.check_if_EC_exists(curr_EC) is False:     # skip this loop-iteration if the EC-ID has already been dis-assigned from the DB
                continue
            TupleList = DB.get_Tuples_of_EC(curr_EC)
            pairings = self.__generate_pairings_from_List(TupleList)
            for pairing in pairings:    # for every Pair of Tuples in the current EC:
                [new_A,new_B,offset] = self.__generate_rotated_ECs(pairing[0], pairing[1])    # do EC-Rotation on them.
                feedback = self.__shallow_new_Tuple_Equality(new_A, new_B)
                if True:
                    if not offset[0]==offset[1]:
                        if not DB.check_if_Tuple_exists(offset):
                            # create a fully new EC:
                            new_EC_id = self.next_EC_id.__str__()
                            DB.set_Tuple_EC(offset, new_EC_id)
                            self.next_EC_id += 1
                result_EC_id = DB.get_EC_of_Tuple(new_A)
                # at this point, A and B are in the same ECs and got conflict-checked, but no rotations generated yet.
                if feedback != "Tuples already in same EC":     # unless the two rotations were already in the same EC, we need to put the result on the T0DO-List
                    todolist.add(result_EC_id)
            if todolist.__len__() == 0:     # if the todolist is empty, stop looping
                break
        # (DONE)

    # DONE, Works---
    def ingest_two_equal_words(self, word_A: str, word_B: str):
        """
        Given two words that are definitively only shifted versions of each other, this
        function will insert all the cross-word Tuple-Equalities.
        """
        wordlen = word_A.__len__()
        wordlen_B = word_B.__len__()
        if wordlen != wordlen_B:
            raise Exception("Inputted Words are not the same length; they cannot be equalized.")
        if wordlen <2:
            raise Exception("Inputted Words are not long enough; they cannot be equalized.")

        for index_left_tuple in range(0, wordlen):
            letr_A1 = word_A[index_left_tuple]
            letr_B1 = word_B[index_left_tuple]
            if (letr_A1==SPACING_letter) or (letr_B1==SPACING_letter):  # skip if this tuple would be a Filler-Tuple
                continue
            Tuple_Left = (letr_A1,letr_B1)
            for index_right_tuple in range(index_left_tuple, wordlen):
                letr_A2 = word_A[index_right_tuple]
                letr_B2 = word_B[index_right_tuple]
                if (letr_A2==SPACING_letter) or (letr_B2==SPACING_letter):  # skip if this tuple would be a Filler-Tuple
                    continue
                Tuple_Right = (letr_A2,letr_B2)
                # Ergo: For every Pair of Cross-Word Tuples:
                if Tuple_Left != Tuple_Right:
                    self.ingest_new_Tuple_Equality(Tuple_Left, Tuple_Right)
                    # also ingest the reversed Tuples, to make the DB become complete quicker:        (dunno if that is actually needed or if those inversals actually happen naturally during this algorithm)
                    Tuple_Left_inverted = (Tuple_Left[1], Tuple_Left[0])
                    Tuple_Right_inverted = (Tuple_Right[1], Tuple_Right[0])
                    self.ingest_new_Tuple_Equality(Tuple_Left_inverted, Tuple_Right_inverted)

    # DONE, Works---
    def ingest_multiple_equal_words(self, wordList: list):
        """
        Does word-equalizing on all words in the list that are ALL the same plaintext words.
        (a.k.a. on all possible two-pairs of words)
        """
        for word_A in wordList:
            for word_B in wordList:
                if word_A != word_B:    # for all distinct pairings of words from the wordlist:
                    self.ingest_two_equal_words(word_A, word_B)     # equalize them

    # DONE, Works--- # TODO CAN I DELETE THIS?   gather_arithmetic_restrictions_DELETE()
    def gather_arithmetic_restrictions_DELETE(self) -> dict:  # TODO CAN I DELETE THIS?
        """
        Returns a Dictionary that assigns a list of Arithmetic Restrictions(ARs) to each EC in the DB.
        """
        allTuples = self.DB.get_global_TupleList()
        EC_AR_mapping = {}  # the future list of gathered ARs, assigned to their respecive start-ECs

        for startTuple in allTuples:
            # --- look for offset-Tuples ---
            for secondTuple in allTuples:
                if startTuple[1] == secondTuple[0]:     # if the second Tuple is like AB+BC:
                    offsetTuple = secondTuple
                    for thirdTuple in allTuples:
                        if (thirdTuple[0] == startTuple[0]
                            and
                            thirdTuple[1] == offsetTuple[1]):

                            resultTuple = thirdTuple

                            # generate the ARs:
                            start_EC = self.DB.get_EC_of_Tuple(startTuple)
                            offset_EC = self.DB.get_EC_of_Tuple(offsetTuple)
                            result_EC = self.DB.get_EC_of_Tuple(resultTuple)
                            newArithmeticRule          = {"start_EC": start_EC, "offset_EC": offset_EC, "result_EC": result_EC}
                            newArithmeticRule_reversed = {"start_EC": offset_EC, "offset_EC": start_EC, "result_EC": result_EC}

                            # insert the AR into the AR-Dict:
                            if start_EC not in EC_AR_mapping.keys():
                                EC_AR_mapping[start_EC] = []  # create an empty Entry for the start-EC, if needed
                            if newArithmeticRule not in EC_AR_mapping[start_EC]:
                                EC_AR_mapping[start_EC].append(newArithmeticRule)

                            # insert the reversed AR into the AR-Dict:
                            if offset_EC not in EC_AR_mapping.keys():
                                EC_AR_mapping[offset_EC] = []  # create an empty Entry for the offset-EC, if needed
                            if newArithmeticRule_reversed not in EC_AR_mapping[offset_EC]:
                                EC_AR_mapping[offset_EC].append(newArithmeticRule_reversed)
        return EC_AR_mapping

    # DONE, Works---
    def gather_arithmetic_restrictions_with_arithmetic_deduplication(self) -> dict:
        """
        Basically gather_arithmetic_restrictions()  BUUUT it automatically only keeps ONE AR of each
        arithmetically equivalent group of ARs.
        (Ergo it is automatically flattened too.)
        BUT broadening is still needed, because I still want need to associate each EC with ALL ARs that are relevant to it.
        """
        allTuples = self.DB.get_global_TupleList()
        EC_AR_mapping = {}  # the future list of gathered ARs, assigned to their respecive start-ECs
        seen_ECTriplets = []


        # DONE, Works---
        def inverse_EC(EC_id: str)->str:
            """
            :returns: The ID of the inversed EC of the input.
            """
            try:
                RepTuple = self.DB.EC_Table[EC_id][0]  # get the first Tuple of that EC
            except KeyError:
                raise Exception(f"EC {EC_id} doesn't exist.")
            reversed_Tuple = (RepTuple[1], RepTuple[0])
            try:
                reversed_EC_id = self.DB.get_EC_of_Tuple(reversed_Tuple)
            except KeyError:
                raise Exception(f"Tuple {reversed_Tuple} doesn't exist.")
            return reversed_EC_id


        # DONE, Works---
        def carefully_insert_AR_into_ECs_ARList(targetECs_ARList: list,
                                                seen_ECTriplets: list,
                                                start_EC: str,
                                                offset_EC: str,
                                                result_EC: str):
            """
             Inserts the given AR smartly into the ECs AR-list, while also making sure that no functional
             duplicates get into the list:
             >Real Duplicates
             >Inverted Duplicates
             >Arithmetic Duplicates
             This is done by keeping track of all seen Triplets ABC and their negatives.

             IMPORANT: I assume that there is only ever ONE arithmetic Relation between such a Triplet, and I'm working
             on the assumption that a properly derived EC-AR-Mapping will follow that law.
            """
            """
            EXPLANATION:
            This check is actually wayy too primitive to detect arithmetical equivalence of ARs.
            BUUT I work under the assumption that it is physically impossible to get two ARs about A,B and C
            have conflicting meaning IF THE ISOMORPHS WERE CORRECTLY INGESTED.
            (I'm not 100% sure, but I think my Isomorph-Ingestion is correct for this purpose.)
            """
            negA = inverse_EC(start_EC)
            negB = inverse_EC(offset_EC)
            negC = inverse_EC(result_EC)
            representative_list = [start_EC, offset_EC, result_EC, negA, negB, negC]
            representative_set = set(representative_list)  # used a set to make it order-independent

            if representative_set in seen_ECTriplets:
                return  # DO NOT INSERT if some re-arrangement is already in some ARList (even of other ECs).
            newArithmeticRule = {"start_EC": start_EC, "offset_EC": offset_EC, "result_EC": result_EC}
            targetECs_ARList.append(newArithmeticRule)
            seen_ECTriplets.append(representative_set)

        for startTuple in allTuples:
            # --- look for offset-Tuples ---
            for secondTuple in allTuples:
                if startTuple[1] == secondTuple[0]:     # if the second Tuple is like AB+BC:
                    offsetTuple = secondTuple
                    for thirdTuple in allTuples:
                        if (thirdTuple[0] == startTuple[0]
                            and
                            thirdTuple[1] == offsetTuple[1]):

                            resultTuple = thirdTuple

                            # generate the ARs:
                            start_EC = self.DB.get_EC_of_Tuple(startTuple)
                            offset_EC = self.DB.get_EC_of_Tuple(offsetTuple)
                            result_EC = self.DB.get_EC_of_Tuple(resultTuple)

                            # insert the AR into the AR-Dict:
                            if start_EC not in EC_AR_mapping.keys():
                                EC_AR_mapping[start_EC] = []  # create an empty Entry for the start-EC, if needed
                            carefully_insert_AR_into_ECs_ARList(targetECs_ARList=EC_AR_mapping[start_EC],
                                                                seen_ECTriplets=seen_ECTriplets,
                                                                start_EC=start_EC,
                                                                offset_EC=offset_EC,
                                                                result_EC=result_EC)
        return EC_AR_mapping

    # DONE, Works---
    def print_EC_AR_mapping(self, EC_AR_mapping: dict):
        """
        (Not used rn I think, but usefull for visual debugging.)
        Simply prints the given mapping in a readable way.
        """
        for EC_id in EC_AR_mapping.keys():
            print(EC_id + ":")
            AR_list = EC_AR_mapping[EC_id]
            for AR in AR_list:
                print(self.__stringify_AR(AR))

    # DONE, Works---
    def print_testWise_ValueAssignment(self, EC_Value_Mapping: dict):
        """
        (Not used rn I think, but usefull for visual debugging.)
        Simply prints the ValueAssignment-DICT in a readable fashion.
        (Replaces Placeholder-"-1"s with ""s)
        """
        for EC in EC_Value_Mapping.keys():
            Value = EC_Value_Mapping[EC]
            if Value == -1:
                Value = ""
            print("[" +EC+ "] \t: " +Value.__str__())

    # DONE, Works---
    def print_EC_AR_mapping_counts(self, EC_AR_mapping: dict):
        """
        (Not used rn I think, but usefull for visual debugging.)
        Simply prints the given mappings AR-amounts for each EC in a readable way.
        """
        for EC_id in EC_AR_mapping.keys():
            ECs_ARs_amount = EC_AR_mapping[EC_id].__len__()
            print(EC_id + "\t:" + ECs_ARs_amount.__str__())

    # DONE, Works---
    def __stringify_AR(self, AR: dict) -> str:
        """
        Used in print_EC_AR_mapping().
        """
        start_EC = AR["start_EC"]
        offset_EC = AR["offset_EC"]
        result_EC = AR["result_EC"]
        return f"{start_EC}+{offset_EC}={result_EC}"

    # DONE, Works---
    def __shallow_new_Tuple_Equality(self, Tuple_A: tuple, Tuple_B: tuple):
        """
        IMPORTANT FUNCTION
        used in ingest_new_Tuple_Equality().
        Puts the two Tuples in the same EC, and does shallow EC-merging if needed and CONFLICT-CHECKING, but nothing more.
        """
        DB = self.DB

        A_exists = DB.check_if_Tuple_exists(Tuple_A)
        B_exists = DB.check_if_Tuple_exists(Tuple_B)

        # if BOTH Tuples already have an EC:
        if A_exists and B_exists:
            # Check if they are already in the same EC:
            EC_A = DB.get_EC_of_Tuple(Tuple_A)
            EC_B = DB.get_EC_of_Tuple(Tuple_B)
            if EC_A == EC_B:
                return "Tuples already in same EC"              # terminate if yes.
            # Do EC-Merging, since they are in different ECs:
            DB.merge_ECs(EC_A, EC_B)    # merge the ECs on a shallow level.

        if A_exists and (not B_exists):
            # just insert B into As existing EC:
            EC_A = DB.get_EC_of_Tuple(Tuple_A)
            DB.set_Tuple_EC(Tuple_B, EC_A)

        if (not A_exists) and B_exists:
            # just insert A into Bs existing EC:
            EC_B = DB.get_EC_of_Tuple(Tuple_B)
            DB.set_Tuple_EC(Tuple_A, EC_B)

        if (not A_exists) and (not B_exists):
            # create a fully new EC:
            #new_EC_id = self.next_EC_id.__str__()
            new_EC_id = self.next_EC_id   # 03.05.2023   SWITCHED TO INTEGER-IDs to speed up ID-comparison  (v13.5   Gen10.2)
            DB.set_Tuple_EC(Tuple_A, new_EC_id)
            DB.set_Tuple_EC(Tuple_B, new_EC_id)
            self.next_EC_id = self.next_EC_id +1

        # at this point, A and B are in the same ECs, but no rotations generated of conflicts checked yet.

        result_ECs_id = DB.get_EC_of_Tuple(Tuple_A)
        Tuplelist = DB.get_Tuples_of_EC(result_ECs_id)
        try:
            conflict = self.__conflict_check_EC(Tuplelist)
            # CONFLICT-CHECKING:
            if conflict is True:
                # Throw some smart Error with like traceable History or some shit.
                TupleListString = DB.niceformat_of_TupleList(Tuplelist)
                raise Exception("CONFLICTING TUPLES in EC:" + TupleListString)
        except:
            #print("EXCEPTION OCCURRED")    # testprint disabled
            #print(Tuple_A)                 # testprint disabled
            #print(Tuple_B)                 # testprint disabled
            #print(result_ECs_id)           # testprint disabled
            #DB.print_EC_Table_detailed()   # testprint disabled
            #DB.print_Tuples_Table()        # testprint disabled
            raise

    # DONE, Works---
    @staticmethod
    def __conflict_check_EC(TupleList: list) -> bool:
        """
        IMPORTANT FUNCTION
        used in __shallow_new_Tuple_Equality().

        Looks at all the Tuples of an EC and checks if they contradict each other due to overlaps.
        (Only a Primitive check that checks for double-assignment of Primary/Secondary Letters)
        False: no Conflict.
        True: CONFLICT.
        """
        for Tuple_A in TupleList:
            for Tuple_B in TupleList:
                if Tuple_A != Tuple_B:              # for every pair of distinct Tuples
                    if Tuple_A[0] == Tuple_B[0]:        # if both FirstLetters are the same: Conflict
                        return True
                    if Tuple_A[1] == Tuple_B[1]:        # if both SecondLetters are the same: Conflict
                        return True
        return False

    # DONE, Works---
    @staticmethod
    def __generate_pairings_from_List(Tuplelist: list) -> list:
        """
        IMPORTANT FUNCTION
        used in ingest_new_Tuple_Equality().

        Generates a List containing all possible pairings of the given Tuplelists Entries.
        (only pairings where A!=B)
        (only ONCE each pairing, to improve runtime)
        """
        resultList = []
        if Tuplelist.__len__() <2:
            raise IndexError("Not enough Tuples in EC.")
        for A in Tuplelist:
            for B in Tuplelist:
                if A==B:
                    continue
                newPairing = (A,B)
                if newPairing not in resultList:
                    resultList.append(newPairing)
        return resultList

    # DONE, Works---
    @staticmethod
    def __generate_rotated_ECs(Tuple_A: tuple, Tuple_B: tuple) -> list:
        """
        Returns a list containing the two resulting Tuples if you rotate the given two Tuples.
        """
        primary_rotation    = (Tuple_A[0], Tuple_B[0])
        secondary_rotation  = (Tuple_A[1], Tuple_B[1])
        offset              = (Tuple_A[1], Tuple_B[0])
        return [primary_rotation, secondary_rotation, offset]



# TODO implement File-Exporting to quicken the whole process of starting up repeated tests (stuff like ECs, ARs)
