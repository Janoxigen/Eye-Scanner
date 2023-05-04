
import random
from typing import Union, Any

import threading  # for Multithreading

# to measure exec time
from timeit import default_timer as timer

from theBackrooms.Cypher_MDA_Analyzer import CypherAnalyzer
from theBackrooms.ValBasedCX import ValBasedCX, conflicting_ECs_Exception

UNDEF_letter = "z"
FILLER_letter = "x"
SPACING_letter = "°"  # (used when supplying Isomorphs into the CX)  (you actually need to change this Variable in the CypherAnalyzer-File too, due to redundancy xdddd)

class myThread (threading.Thread):
    """
    This class is only for the purpose of multithreading the conflict-checking in each recursion.
    """
    def __init__(self,
                 CX: CypherAnalyzer,
                 alphLen: int,
                 targetEC: str,
                 ECvalue: int,
                 ActionList: list,
                 baseAssignments: dict,
                 threadLock: threading.Lock,
                 shared_output: list):
        threading.Thread.__init__(self)
        self.CX = CX
        self.alphLen = alphLen
        self.targetEC = targetEC
        self.ECvalue = ECvalue
        self.ActionList = ActionList
        self.baseAssignments = baseAssignments
        self.threadLock = threadLock
        self.shared_output = shared_output

    def run(self):
        AlphGeneratorGen10_2.conflict_check_new_choice(self.CX,
                                                       self.alphLen,
                                                       self.targetEC,
                                                       self.ECvalue,
                                                       self.ActionList,
                                                       self.baseAssignments,
                                                       self.threadLock,
                                                       self.shared_output)

class AlphGeneratorGen10_2:

    # DONE, Works---
    @staticmethod
    def generate_working_EC_Value_Assignment(CX: CypherAnalyzer,
                                             alphLen: int,
                                             realTODOlist=None,
                                             baseAssignments=None,
                                             ActionListsList=None,
                                             recursionLevel=0,
                                             threadLock=None):
        """
        Systematically searches for a FULL EC-Value-Assignment that doesn't cause a
        contradiction during AR-Testing.
        :param realTODOlist    (for recursion purposes, ignore if using the function as an initializer.) [str]
        :param baseAssignments (for recursion purposes, ignore if using the function as an initializer.) {str->int}
        :param ActionListsList (for recursion purposes, ignore if using the function as an initializer.) [[tuple]]
        :param threadLock   (for recursion purposes, ignore if using the function as an initializer.)
        :param recursionLevel is just for Testprnts
        :returns: A EC-Value-DICT:  EC->int
        """
        # --- if this is the initializer: --- (a.k.a. the topmost recursion)
        if realTODOlist==None:
            # ------ gather all the ARs ------
            print("gathering ARs... (this might take a while)")  # testprint
            timerStart = timer()    # for testprints
            EC_AR_mapping = CX.gather_arithmetic_restrictions_with_arithmetic_deduplication()
            print(f"{timer() - timerStart} seconds for AR-gathering")   # testprint
            AR_amout = 0    # for testprints
            for EC in EC_AR_mapping.keys():  # for testprints
                AR_amout += EC_AR_mapping[EC].__len__()  # for testprints
            print(f"gathered {AR_amout} ARs (already arithmetically deduplicated).")   # testprint
            EC_AR_mapping = AlphGeneratorGen10_2.broaden_EC_AR_Mapping(EC_AR_mapping)
            print("finished broadening those ARs.")  # testprint
            # ------ prepare the baseAssignments-Dict ------
            baseAssignments = {}
            for EC in CX.DB.EC_Table.keys():
                baseAssignments[EC] = -1
            # ------ generate the T0DOlist ------
            # -- sort all ECs by their size (decreasing) --
            EC_Table_tupled = [(EC, Tuples) for EC, Tuples in CX.DB.EC_Table.items()]   # converts the Dictionary into a Tuple-List  (Key,Value)
            def EC_size(dictEntry: tuple):
                return dictEntry[1].__len__()
            EC_Table_tupled.sort(key=EC_size, reverse=True)
            print(f"ECsizes={[Tuples.__len__() for EC, Tuples in EC_Table_tupled]}")  # testprint
            sizesortedEClist = [EC for EC, Tuples in EC_Table_tupled]  # extract the ECs that these numbers represent
            print(f"EC-IDs ={sizesortedEClist}")  # testprint
            # -- determine the Assignment-Progression by analyzing the ARs --
            realTODOlist = AlphGeneratorGen10_2.determine_TODO_Progression(CX, sizesortedEClist, EC_AR_mapping)
            print(f"TODOlst={realTODOlist}")  # testprint
            # -- determine the ActionList of each Iteration by analyzing the ARs --
            ActionListsList = AlphGeneratorGen10_2.determine_ARtesting_progression(CX, EC_AR_mapping, TODOprogression=realTODOlist)
            # ------ prepare the Threadlock for Multithreading ------
            threadLock = threading.Lock()
        # --- RECURSION-ANKER: no more ECs in T0DO-List ---
        if realTODOlist.__len__()==0:
            return baseAssignments
        # ------ REGULAR RECURSION: ------
        print(f"{' '*recursionLevel}{recursionLevel}")    # testprint
        currEC = realTODOlist.pop(0)
        if recursionLevel==0:
            ValueList=[1]  # the very first EC need to be tested for only one Value, since all those solutions are equally valid/invalid.
        else:
            ValueList = list(range(1, alphLen))
        # ------ MULTITHREADED CONFLICT-CHECK: ------
        shared_output = []
        threads = []
        for currVal in ValueList:
            newThread = myThread(CX,
                                 alphLen,
                                 currEC,
                                 currVal,
                                 ActionListsList[recursionLevel],
                                 baseAssignments,
                                 threadLock,
                                 shared_output)
            newThread.start()
            threads.append(newThread)
        # Wait for all threads to complete
        for t in threads:
            t.join()
        # ------ RECURSION FOR WORKING VALUES in shared_output: ------
        newRecursionLevel = recursionLevel+1
        #random.shuffle(shared_output)  # TODO YOU CAN UN-COMMENT THIS, IF YOU WANT IT TO ALWAYS TAKE A DIFFERENT ROUTE EACH TIME YOU RUN THIS PROGRAM.

        # -------------------------------
        # ------- UNSHUFFLED MODE -------
        # Note: This mode sorts the validValueList to always be small-to-big (used for speed-comparisons).
        # YOU CAN UNCOMMENT THIS TO *ALWAYS* HAVE EXACTLY THE SAME ORDER IN WHICH THE PROGRAM TESTS VALUES.
        """
        def EC_value(entry: tuple):
            assignments = entry[1]
            return assignments[currEC]

        shared_output.sort(key=EC_value, reverse=False)
        """
        # ----- UNSHUFFLED MODE END -----
        # -------------------------------

        for entry in shared_output:
            currAssignments = entry[1]
            # --- RECURSION: ---
            retVal = AlphGeneratorGen10_2.generate_working_EC_Value_Assignment(CX,
                                                                            alphLen,
                                                                            realTODOlist.copy(),
                                                                            currAssignments,
                                                                            ActionListsList,
                                                                            newRecursionLevel,
                                                                            threadLock)
            if retVal=="fail":
                continue  # if recursion was total fail, go next candidate number
            else:
                return retVal  # return the found working currAssignment to the upper recursions.
        # --- if reached here, it means that none of the non-conflicting Value Choices (if any exist at all) have succeded in their sub-recursions. ---
        return "fail"

    # DONE, Works---
    @staticmethod
    def determine_ARtesting_progression(CX: CypherAnalyzer, EC_AR_mapping: dict, TODOprogression: list) -> list:
        """
        ((implemented in Gen10))
        Simulates ALL the Recursion-Levels and determines which exact new pinnings and AR-Conflict-checks happen on each one.
        The Actions in the output-Lists are DICTS, encoded in two possible ways:
            >new pinnings: three EC-IDs, A,B and C, where A+B->C
            >AR-Conflict-checks: three EC-IDs, A,B and C, where A+B==C
        The types can be distinguished by checking the "type" entry of the DICT, which is either "newPin" or "confCheck".
        (For performance reasons I will instead be using a field "newPin" that is True or False.)
        (For Performance reasons I will use a static Tuple instead of a DICT.)
            [0] is the bool "newPin"
            [1] is A
            [2] is B
            [3] is C

        NOTE: just like in determine_TODO_Progression, this one also needs to have the EC-AR-Mapping "broadened" beforehand.

        :returns: A List of Lists, one for each Level, with the exact Order of Actions.
        """

        # DONE, Works---
        def inverse_EC(CX: CypherAnalyzer, EC_id: str)->str:
            """
            :returns: The ID of the inversed EC of the input.
            """
            try:
                RepTuple = CX.DB.EC_Table[EC_id][0]  # get the first Tuple of that EC
            except KeyError:
                raise Exception(f"EC {EC_id} doesn't exist.")
            reversed_Tuple = (RepTuple[1], RepTuple[0])
            try:
                reversed_EC_id = CX.DB.get_EC_of_Tuple(reversed_Tuple)
            except KeyError:
                raise Exception(f"Tuple {reversed_Tuple} doesn't exist.")
            return reversed_EC_id

        # DONE, Works---
        def pin_EC(CX: CypherAnalyzer, EC_id: str, pinned_mapping: dict, EC_ToDoList: list):
            """
            Simply pin the given EC, but ALSO pin the inverted EC.
            (Assumes that the EC has a Tuple in it already and the inverted EC exists.)

            Note: This Version also adds the reversed EC to the T0DOlist. (that's the reason I moved the T0DOList-Editing to in here.)
            """
            reversed_EC_id = inverse_EC(CX, EC_id)

            pinned_mapping[EC_id] = True
            pinned_mapping[reversed_EC_id] = True

            EC_ToDoList.append(EC_id)
            EC_ToDoList.append(reversed_EC_id)

        # DONE, Works---
        def carefully_insert_checkAction_into_ActionList(CX: CypherAnalyzer,
                                                         ActionList: list,
                                                         seen_checkTriplets: list,
                                                         EC_A: str,
                                                         EC_B: str,
                                                         EC_C: str):
            """
             Inserts the given Check-Action smartly into the Actionlist, while also making sure that no functional
             duplicates get into the list:
             >Real Duplicates
             >Inverted Duplicates
             >Arithmetic Duplicates
             This is done by keeping track of all seen Triplets ABC and their negatives.

             TODO: Maybe I don't even need to check for arithmetic Duplicates here, if I already made sure to
              not have any arithmetically duplicate ARs...

             IMPORANT: I assume that there is only ever ONE arithmetic Relation between such a Triplet, and I'm working
             on the assumption that a properly derived EC-AR-Mapping will follow that law.
            """
            negA = inverse_EC(CX, EC_A)
            negB = inverse_EC(CX, EC_B)
            negC = inverse_EC(CX, EC_C)
            representative_list = [EC_A, EC_B, EC_C, negA, negB, negC]
            representative_set = set(representative_list)  # used a set to make it order-independent

            if representative_set in seen_checkTriplets:
                return  # DO NOT INSERT if some re-arrangement is already in the ActionList.
            ActionList.append((False, EC_A, EC_B, EC_C))  # A+B= C
            seen_checkTriplets.append(representative_set)


        # DONE, Works---
        def single_iteration_analysis(CX: CypherAnalyzer, EC_AR_mapping: dict, pinned_mapping: dict, target_EC: str) -> list:
            """
            Determines the ActionList of a singular Iteration by doing abstract AR-Testing and keeping track of
            the exact order of new pinnings and Conflict-Checks.

            :returns: The ActionList of that specific Iteration (see docstring of the function surrounding this one.)

            NOTE: technically I can easily combine this with the T0DO-Progression-finding but for
            debugging purposes i will keep them separated for now.
            :param pinned_mapping needs to be a dict of [EC->Bool]
            """

            actionList = []

            # seen_checkTriplets is a documentation of what Triplets ABC have already been seen.
            # It doesn't matter if A+B=C  or -A-B=-C  or  C-B=A...
            # the result will always be the entry (A,B,C,-A,-B,-C)  in this List
            seen_checkTriplets = []

            # Note: no longer using a set for the T0DOlist because with the broadened ARs and not-usage of
            # a dirtyGraph, there is no possibility of an already newly pinned EC to be pinned again and inserted
            # a second time into the T0DOlist.)
            EC_ToDoList = []

            # Pin the User-chosen EC:
            pin_EC(CX, target_EC, pinned_mapping, EC_ToDoList)

            while True:  # (loop until T0DO-List is empty)
                if EC_ToDoList.__len__() == 0:
                    break
                curr_EC = EC_ToDoList.pop(0)
                for curr_AR in EC_AR_mapping[curr_EC]:
                    EC_A = curr_AR["start_EC"]
                    EC_B = curr_AR["offset_EC"]
                    EC_C = curr_AR["result_EC"]

                    A_pinned = pinned_mapping[EC_A]
                    B_pinned = pinned_mapping[EC_B]
                    C_pinned = pinned_mapping[EC_C]

                    if A_pinned and B_pinned:
                        if C_pinned:
                            # put a conflict-check into the ActionList.
                            carefully_insert_checkAction_into_ActionList(CX, actionList, seen_checkTriplets, EC_A, EC_B, EC_C)
                        if not C_pinned:
                            pin_EC(CX, EC_C, pinned_mapping, EC_ToDoList)
                            # put a newPin into the ActionList.
                            newAction = (True, EC_A, EC_B, EC_C)  #  A+B -> C
                            actionList.append(newAction)
                    elif C_pinned:
                        if A_pinned:
                            pin_EC(CX, EC_B, pinned_mapping, EC_ToDoList)
                            # put a newPin into the ActionList.
                            negA = inverse_EC(CX, EC_A)
                            newAction = (True, EC_C, negA, EC_B)  #  C-A -> B
                            actionList.append(newAction)
                        if B_pinned:
                            pin_EC(CX, EC_A, pinned_mapping, EC_ToDoList)
                            # put a newPin into the ActionList.
                            negB = inverse_EC(CX, EC_B)
                            newAction = (True, EC_C, negB, EC_A)  #  C-B -> A
                            actionList.append(newAction)
            return actionList

        # --- Prepare the overall List and an empty pinnedList. ---
        iterationListsList = []  # This list will contain each Iterations Action-List
        pinned_mapping = {}
        for EC in CX.DB.EC_Table.keys():
            pinned_mapping[EC]=False

        print("ActionCounts for each stage:")  # testprint
        counter=0  # for testprints

        # --- do Analysis and return Result. ---
        for currEC in TODOprogression:
            actionList = single_iteration_analysis(CX, EC_AR_mapping, pinned_mapping, target_EC=currEC)
            iterationListsList.append(actionList)
            print(f"{counter}={actionList.__len__()}")  # testprint
            counter+=1  # for testprints
        return iterationListsList

    # DONE, Works---
    @staticmethod
    def determine_TODO_Progression(CX: CypherAnalyzer, sizesortedEClist: list, EC_AR_mapping: dict) -> list:
        """
        Returns the exact ECs that are Choice-Points during the Recursion.
        In other words: Because pinning an EC to ANY Value will ALWAYS have the same pinning-effect on
        other ECs, as a result of which our Gen8-Recursion will always go through the T0DO-List in
        exactly the same progression.
        ERGO: we can just simulate that progression once and then spare us the stupid T0DO-List-Updating on runtime.

        NOTE: just like in the real Gen8 AR-Testing, this one also needs to have the EC-AR-Mapping "broadened" beforehand.
        """

        # DONE, Works---
        def remove_from_unpinnedList(EC_to_remove: str):
            """
            Removes the given EC-id from the unpinned-List
            """
            try:
                remaining_TODOlist.remove(EC_to_remove)
            except ValueError:
                pass

        # DONE, Works---
        def pin_EC(CX: CypherAnalyzer, EC_id: str, pinned_mapping: dict, EC_ToDoList: set):
            """
            Simply pin the given EC, but ALSO pin the inverted EC.
            (Assumes that the EC has a Tuple in it already and the inverted EC exists.)

            Note: This Version also adds the reversed EC to the T0DOlist. (that's the reason I moved the T0DOList-Editing to in here.)
            """
            try:
                RepTuple = CX.DB.EC_Table[EC_id][0]  # get the first Tuple of that EC
            except KeyError:
                raise Exception(f"EC {EC_id} doesn't exist.")
            reversed_Tuple = (RepTuple[1], RepTuple[0])
            try:
                reversed_EC_id = CX.DB.get_EC_of_Tuple(reversed_Tuple)
            except KeyError:
                raise Exception(f"Tuple {reversed_Tuple} doesn't exist.")

            pinned_mapping[EC_id] = True
            pinned_mapping[reversed_EC_id] = True

            remove_from_unpinnedList(EC_id)
            remove_from_unpinnedList(reversed_EC_id)

            EC_ToDoList.add(EC_id)
            EC_ToDoList.add(reversed_EC_id)

        # DONE, Works---
        def abstract_AR_testing(CX: CypherAnalyzer, pinned_mapping: dict, EC_AR_mapping: dict, dirtyEC):
            """
            Basically AR-Testing but without Values, only focusing on the pinning itself.
            ALSO: edits the remaining_TODOlist, by removing the newly pinned ECs.
            ALSO: edits the pinnedMapping.
            :param pinned_mapping needs to be a dict of [EC->Bool]
            """

            EC_ToDoList = set()  # using a set for innate duplicate-prevention

            # Pin the User-chosen EC:
            pin_EC(CX, dirtyEC, pinned_mapping, EC_ToDoList)

            while True:  # (loop until T0DO-List is empty)
                if EC_ToDoList.__len__() == 0:
                    break
                curr_EC = EC_ToDoList.pop()
                for curr_AR in EC_AR_mapping[curr_EC]:
                    EC_A = curr_AR["start_EC"]
                    EC_B = curr_AR["offset_EC"]
                    EC_C = curr_AR["result_EC"]

                    A_pinned = pinned_mapping[EC_A]
                    B_pinned = pinned_mapping[EC_B]
                    C_pinned = pinned_mapping[EC_C]

                    if A_pinned and B_pinned:
                        if not C_pinned:
                            pin_EC(CX, EC_C, pinned_mapping, EC_ToDoList)
                    elif C_pinned:
                        if A_pinned:
                            pin_EC(CX, EC_B, pinned_mapping, EC_ToDoList)
                        if B_pinned:
                            pin_EC(CX, EC_A, pinned_mapping, EC_ToDoList)

        remaining_TODOlist = sizesortedEClist.copy()
        todoProgression = []
        # prepare the empty pinned-mapping:
        pinned_mapping = {}
        for EC in sizesortedEClist:
            pinned_mapping[EC]=False

        while remaining_TODOlist.__len__() > 0:  # While there is still ECs in the T0DOlist:
            currEC = remaining_TODOlist.pop(0)
            todoProgression.append(currEC)
            abstract_AR_testing(CX, pinned_mapping, EC_AR_mapping, dirtyEC=currEC)

        return todoProgression

    # DONE, Works---
    @staticmethod
    def conflict_check_new_choice(CX: CypherAnalyzer,
                                  alphLen: int,
                                  targetEC: str,
                                  ECvalue: int,
                                  ActionList: list,
                                  baseAssignments: dict,
                                  threadLock: threading.Lock,
                                  shared_output: list):
        """
        A single Thread of the Multithreaded Conflict-check.
        It tests only one Value for the given EC and adds the results to the shared_output (only if no conflict).
        Each Entry of the shared_output is a Tuple:
            [0]  == resulting oldTODOlist  (( ACTUALLY "None" since Gen9 ))
            [1]  == resulting Assignments
        (I don't need to save the EC or the Value that caused this result, cuz that is already inside the
        assignments and doesn't matter for the Recursion.)
        :param shared_output: A list of the results of NON-CONFLICTING Values (as Tuple).
        """
        rev_targetEC = AlphGeneratorGen10_2.find_reversed_EC(CX, targetEC)
        # --- prepare new Lists ---
        currAssignments = baseAssignments.copy()  # is this even enough deepness for a copy??
        currAssignments[targetEC] = ECvalue  # add the current attempted Value-assignment to the List.
        currAssignments[rev_targetEC] = (-1*ECvalue)%alphLen  # (and the inversed ECs Value)
        # --- initial Tuple-Contradiction-Check ---  (to quickly find OBVIOUS contradictions)
        # (inversed Check not needed, assuming that ECs and their Values are fully developed.)
        retVal = AlphGeneratorGen10_2.check_for_Tuple_Conflicts(CX, currAssignments, alphLen, toCheck_Values=[ECvalue])
        if retVal=="conflict":
            return
        # --- do AR-testing ---
        retVal = AlphGeneratorGen10_2.AR_testing(CX,
                                              ActionList,
                                              currAssignments,
                                              alphLen=alphLen)
        if retVal=="contradiction":
            return
        currAssignments = retVal
        # --- Tuple-Contradiction-Check ---
        retVal = AlphGeneratorGen10_2.check_for_Tuple_Conflicts(CX, currAssignments, alphLen)
        if retVal=="conflict":
            return
        # --- RETURN OF SUCCESSFULL ASSIGNMENT: ---
        entry = (None, currAssignments)  # TODO drop the outdated tuple-format, it's no longer needed
        threadLock.acquire(blocking=True)
        shared_output.append(entry)
        threadLock.release()
        return

    # DONE, Works---
    @staticmethod
    def find_reversed_EC(CX: CypherAnalyzer, EC_id: str) -> str:
        """
        Returns the EC-ID of the inverted EC.
        (Assumes that the EC has a Tuple in it already.)
        """
        try:
            RepTuple = CX.DB.EC_Table[EC_id][0]  # get the first Tuple of that EC
        except KeyError:
            raise Exception(f"EC {EC_id} doesn't exist.")
        reversed_Tuple = (RepTuple[1], RepTuple[0])
        try:
            reversed_EC_id = CX.DB.get_EC_of_Tuple(reversed_Tuple)
        except KeyError:
            raise Exception(f"Tuple {reversed_Tuple} doesn't exist.")
        return reversed_EC_id

    # DONE, Works---
    @staticmethod
    def AR_testing(CX: CypherAnalyzer,
                   ActionList: list,
                   base_assignments: dict,
                   alphLen: int) -> Union[str, dict[Any, int]]:
        """
        Gen10 AR-Testing is different from the original because it doesn't search for Conclusions in the ARs but
        gets a pre-determined List of Actions that it has to perform.

        Just like Gen9-AR-Testing, Gen10 doesn't keep track of the changes in the T0DO-list, since the concept of
        a dynamically-determined T0DOlist was dropped.

        IMPORTANT:
        Since Gen10, the base-assignments-dict will be taken as-is as an EC_Value_Mapping.
        a.k.a. it won't be smartly ingested, to save performance.
        That means that it needs to fulfill the following:
            1: EVERY EC MUST BE EITHER ASSIGNED OR HAVE "-1".
            2: NEW ASSIGNMENTS MUST BE MANUALLY "invertedly completed".
        IT WILL BE EDITED, SO YOU NEED TO MAKE A BACKUP OF THE ASSIGNMENTS YOURSELF PRIOR TO THIS FUNCTION.

        NOTE: DIRTYGRAPH NOT NEEDED since Gen6:
        Since the EC-AR-Mapping is "broadened", we only need to dirty the actually
        dirty-causing EC.

        :returns: "contradiction" if Error, else the EC-Values-Dict.
        """

        EC_Value_Mapping = base_assignments  # copying doesn't need to be done since Gen10, cuz base_assignments needs to be backupped by the caller themselves.

        # DONE, Works---
        def assign_EC_Value(EC_id: str, value: int):
            """
            Simply assign the given Value to the given EC, but ALSO assign the inverted Value to the inverted EC.
            (Only causes Values that are within the 0-83 range because of mod83)
            (Assumes that the EC has a Tuple in it already.)
            """
            try:
                RepTuple = CX.DB.EC_Table[EC_id][0]  # get the first Tuple of that EC
            except KeyError:
                raise Exception(f"EC {EC_id} doesn't exist.")
            reversed_Tuple = (RepTuple[1], RepTuple[0])
            try:
                reversed_EC_id = CX.DB.get_EC_of_Tuple(reversed_Tuple)
            except KeyError:
                raise Exception(f"Tuple {reversed_Tuple} doesn't exist.")
            reversed_Value = (value * -1) % alphLen

            EC_Value_Mapping[EC_id] = value
            EC_Value_Mapping[reversed_EC_id] = reversed_Value

        for Action in ActionList:
            EC_A = Action[1]
            EC_B = Action[2]
            EC_C = Action[3]
            Val_A = EC_Value_Mapping[EC_A]
            Val_B = EC_Value_Mapping[EC_B]
            # TODO maybe add a "-1" -check to catch coding errors where I supplied the wrong baseAssignments or ActionList.
            #  but for performance reasons I will ignore that check and hope that it won't bite me in the ass.

            actionType_is_newPin = Action[0]
            if actionType_is_newPin:
                Val_C = (Val_A + Val_B) % alphLen
                assign_EC_Value(EC_C, Val_C)
            else:  #  actionType == conflictCheck
                Val_C = EC_Value_Mapping[EC_C]
                expected_C_Val = (Val_A + Val_B) % alphLen
                if Val_C != expected_C_Val:  # if we already concluded that the Value must have been something else...
                    return "contradiction"
                else:  # C-Val == expected-Val
                    pass

        return EC_Value_Mapping

    # DONE, Works---
    @staticmethod
    def broaden_EC_AR_Mapping(EC_AR_mapping: dict) -> dict:
        """
        Returns an EC-AR-Mapping that lists for each EC a list of ALL ARs that contain
        said EC at ANY position.
        That means that each AR is associated to three ECs.

        Note: optimally this is called on an already flattened EC-AR-Mapping to
        not cause pointless rephrasings of ARs.
        """
        new_EC_AR_mapping = {}
        all_ECs = EC_AR_mapping.keys()
        # --- create emptyLists for all ECs: ---
        for EC in all_ECs:
            new_EC_AR_mapping[EC] = []
        # --- fill in all the ARs: ---
        for EC in all_ECs:
            ECs_ARs_list = EC_AR_mapping[EC]
            for AR in ECs_ARs_list:
                EC_A = AR["start_EC"]
                EC_B = AR["offset_EC"]
                EC_C = AR["result_EC"]
                new_EC_AR_mapping[EC_A].append(AR)
                new_EC_AR_mapping[EC_B].append(AR)
                new_EC_AR_mapping[EC_C].append(AR)
        return new_EC_AR_mapping

    # DONE, Works---
    @staticmethod
    def check_for_Tuple_Conflicts(CX: CypherAnalyzer, EC_Value_Mapping: dict, alphLen: int, toCheck_Values=None) -> str:
        """
        Checks if this current EC-Value mapping assigns two ECs the same Value despite
        them having two Tuples that are IMPOSSIBLE together.
        (Same primary or secondary letter.)

        Example:
        [AB, EF, XY]    can't be the same Value as
        [AC, HI, LP]    cuz of AB and AC.

        ALSO RETURNS "conflict" if an EC was assigned "0".
        :param toCheck_Values (List of Vals) - only checks the Value(s) given.
        :returns: "conflict" or "NO conflict"
        """
        # for Speed-Improvement purposes, I do this dirtyList-IF only once and then have two Versions of
        # this Function: one with no dirtyList and one with a dirtyList Provided.
        if toCheck_Values==None:
            # --- prepare the inversed ValueMapping ---
            Tuples_of_each_Value_dict = {}
            for i in range(1, alphLen):
                Tuples_of_each_Value_dict[i]=[]
            for EC in EC_Value_Mapping.keys():
                Val = EC_Value_Mapping[EC]
                if Val == 0:
                    return "conflict"
                if Val != -1:
                    # add this ECs Tuples to the List of it's Value's Tuples.
                    # (this doesn't cause duplicates, unless a Tuple is in two ECs at the same time.)
                    Tuples_of_each_Value_dict[Val].extend(CX.DB.get_Tuples_of_EC(EC))
            # --- check each Value for conflicting ECs. ---
            for Val in Tuples_of_each_Value_dict.keys():
                Tuples = Tuples_of_each_Value_dict[Val]
                pairings = AlphGeneratorGen10_2.all_distinct_pairings(Tuples)
                # -- for every pair of distinct Tuples that have this Value: --
                for pairing in pairings:
                    # TODO maybe i could improve performance by reversing this search:
                    #  >only check for each firstLetter if there, among the Tuples with the same FirstLetter, there
                    #   is one with the same Value.
                    #  >can easily be done using the DBs funny Tuple-Table-Dictionary-structuring.
                    #       >(the Tupletable is structured like this:  {firstletter->{secondletter->EC}})
                    #  >this ONLY WORKS IF i assume that the ECs have been fully developed (meaning that
                    #   reverse ECs contain ALL the reversed Tuples of the original one, which allows me to scan only for firstletter-overlaps.)
                    Tuple_A = pairing[0]
                    Tuple_B = pairing[1]
                    # (equals-check not needed cuz I assume that no duplicatesd Tuples can happen and the pairing-functions doesn't cause self-pairing.)
                    # -- check if the firstLetter or lastLetter are the same (ergo conflict) --
                    if (Tuple_A[0]==Tuple_B[0]) or (Tuple_A[0]==Tuple_B[0]):
                        return "conflict"
            return "NO conflict"
        else: # if toCheck_Values was provided:
            # --- prepare the inversed ValueMapping ---
            Tuples_of_each_Value_dict = {}
            for i in toCheck_Values:
                Tuples_of_each_Value_dict[i]=[]
            for EC in EC_Value_Mapping.keys():
                Val = EC_Value_Mapping[EC]
                if Val == 0:
                    return "conflict"
                if Val != -1:
                    if Val in toCheck_Values:
                        # add this ECs Tuples to the List of it's Value's Tuples.
                        # (this doesn't cause duplicates, unless a Tuple is in two ECs at the same time.)
                        Tuples_of_each_Value_dict[Val].extend(CX.DB.get_Tuples_of_EC(EC))
            # --- check each Value for conflicting ECs. ---
            for Val in toCheck_Values:
                Tuples = Tuples_of_each_Value_dict[Val]
                pairings = AlphGeneratorGen10_2.all_distinct_pairings(Tuples)
                # -- for every pair of distinct Tuples that have this Value: --
                for pairing in pairings:
                    Tuple_A = pairing[0]
                    Tuple_B = pairing[1]
                    # (equals-check not needed cuz I assume that no duplicates can happen and the pairing-functions doesn't cause self-pairing.)
                    # -- check if the firstLetter or lastLetter are the same (ergo conflict) --
                    if (Tuple_A[0]==Tuple_B[0]) or (Tuple_A[0]==Tuple_B[0]):
                        return "conflict"
            return "NO conflict"

    # DONE, Works---
    @staticmethod
    def all_distinct_pairings(List: list) -> list:
        """
        :returns: a List of all possible Pairs(Tuples),, EXCLUDING reorderings of existing Tuples and self-pairings.
        """
        resultList = []
        ListSize = List.__len__()
        for i in range(0, ListSize):
            for j in range(i+1, ListSize):
                resultList.append(  (List[i],List[j])  )
        return resultList


    # DONE, Works---
    @staticmethod
    def print_ECvalueMapping_invertedly(EC_Value_Mapping: dict, alphLen: int):
        """
        Simply prints an EC-Valuemapping in an inverted way (as each Value's EC-List).
        used in GENERATE_ALPHABET_GEN10_2()
        """
        # --- prepare the inversed ValueMapping ---
        ECs_of_each_Value_dict = {}
        for i in range(-1, alphLen):
            ECs_of_each_Value_dict[i]=[]
        for EC in EC_Value_Mapping.keys():
            Val = EC_Value_Mapping[EC]
            ECs_of_each_Value_dict[Val].append(EC)
        # --- print ---
        for Val in ECs_of_each_Value_dict.keys():
            ECs_string = ""
            first = True
            for EC in ECs_of_each_Value_dict[Val]:
                if not first:
                    ECs_string += ", "
                else:
                    first=False
                ECs_string += str(EC)
            print(f"{Val}= "+ECs_string)

    # DONE, Works---
    @staticmethod
    def convert_ECvalAssignment_to_TupleValAssignment(CX: CypherAnalyzer, EC_Value_Mapping: dict) -> dict:
        """
        Converts the given  EC->Value mapping into a Tuple->Value mapping.
        Used to convert the EC-Value-Mapping that is generated by  generate_working_EC_Value_Assignment()  into a
        Tuple-Value-Mapping that is inputtable into a VBCX.
        """
        TupleMapping = {}
        for EC in EC_Value_Mapping.keys():
            Value = EC_Value_Mapping[EC]
            ECs_Tuples = CX.DB.get_Tuples_of_EC(EC)
            for Tuple in ECs_Tuples:
                TupleMapping[Tuple] = Value
        return TupleMapping

    # DONE, Works---
    @staticmethod
    def fill_VBCX_with_TupleValAssignment(VBCX: ValBasedCX, Tuple_Value_Mapping: dict):
        """
        Fills the given VBCX with the given Tuple-Value-Assignment.
        """
        for Tuple in Tuple_Value_Mapping.keys():
            Value = Tuple_Value_Mapping[Tuple]
            retval = VBCX.ingest_new_Tuple_Assignment(Tuple, Value)
            if retval=="CONFLICTING TUPLES":
                raise conflicting_ECs_Exception()
        VBCX.extrapolate_all_Tuples()

    # DONE, Works---
    @staticmethod
    def decide_relevancy_of_letters(list_of_Isomorph_lists: list, alphabet: str) -> tuple:
        """
        Splits the alphabet into two Lists of letters, with the "relevant" Group
        being the Letters which appear in at least one Isomorph.
        :param list_of_Isomorph_lists [[str]]
        :returns: a Tuple with (relevantLetters, pointlessLetters)
        """
        relevant_letters = ""
        for IsomorphGroup in list_of_Isomorph_lists:
            for Isomorph in IsomorphGroup:
                for letter in Isomorph:
                    if letter != SPACING_letter:
                        if letter not in relevant_letters:
                            relevant_letters += letter
        pointless_letters = ""
        for letter in alphabet:
            if letter not in relevant_letters:
                pointless_letters += letter
        return (relevant_letters, pointless_letters)

    # DONE, Works---
    @staticmethod
    def generate_alphabet_from_VBCX(VBCX: ValBasedCX,
                                    remaining_possible_letters: str,
                                    alphLen: int,
                                    fillerLetters: str,
                                    partial_alphabet=None):
        """
        Returns an Alphabet that fulfills the supplied VBCXs ECs.
        :param remaining_possible_letters ONLY GIVE ME THE RELEVANT LETTERS THAT AREN'T FILLERS.
        :param fillerLetters only needed at the end, when filling in the Fillers.
        :param partial_alphabet for Recursion-Purposes, ignore if calling from outside.
        """
        # ---- ANKER ----
        if remaining_possible_letters.__len__() == 0:
            result_alphabet = AlphGeneratorGen10_2.fill_in_undefs(partial_alphabet, fillerLetters)
            return result_alphabet
        # ---- INITIATOR ----
        if partial_alphabet==None:
            partial_alphabet = UNDEF_letter * alphLen  # gives you "zzzzzzzz"....
        # ---- RECURSION ----
        # -- find first editeableFreespot --
        toEdit_index = -1
        for i in range(0, partial_alphabet.__len__()):
            if partial_alphabet[i]==UNDEF_letter:
                toEdit_index=i
                break
        if toEdit_index == -1:
            raise Exception("somehow we filled the entire Alph but still have letters to do.")
        # -- do the letter-trying --
        for i in range(0, remaining_possible_letters.__len__()+1):
            if i == remaining_possible_letters.__len__():
                curr_try_letter = FILLER_letter  # use the fillerLetter as the last hope before giving up on this recursion
            else:
                curr_try_letter = remaining_possible_letters[i]
            # (actually removing the letter comes later, since the VBCX-conclusions might remove even more letters)
            # -- insert current try-letter into partial Alphabet: --
            new_alph = list(partial_alphabet)
            new_alph[toEdit_index] = curr_try_letter
            new_alph = "".join(new_alph)  # re-convert to String
            # -- VBCX-based conclusion of other pinned letters. --
            new_alph = AlphGeneratorGen10_2.VBCX_based_letterConcluding(VBCX, new_alph, alphLen)
            if new_alph == "contradiction":
                continue  # if conflict, go next letter
            # -- if not conflict: do recursion --
            # but first, determine what letter-options remain:
            new_restList = ""
            for letr in remaining_possible_letters:
                if letr not in new_alph:
                    new_restList += letr
            # -- recursion: --
            result = AlphGeneratorGen10_2.generate_alphabet_from_VBCX(VBCX,
                                                                   new_restList,
                                                                   alphLen,
                                                                   fillerLetters,
                                                                   partial_alphabet=new_alph)
            if result=="failure to find ANY possible Alphabet (in this recursion setup)":
                continue
            return result  # this return is only reached if the recursions were a success.
        return "failure to find ANY possible Alphabet (in this recursion setup)"  # this return is only reached if all possible letter choices failed.

    # DONE, Works---
    @staticmethod
    def VBCX_based_letterConcluding(VBCX: ValBasedCX, partial_alphabet: str, alphLen: int) -> str:
        """
        Used in generate_alphabet_from_VBCX().

        When given a partial Alphabet, it uses Tuple-Values of the VBCX to assign Posses to Letters.
        If a newPinned Location is free: insert.
        If a newPinned Location is occupied: conflict.

        :returns: "contradiction" if Error, else the partial Alphabet, but with all new Letters Inserted where Possible.

        Note: That means that the list of unassigned letters is out of sync after running this Function, so it needs to be re-scanned.
        """
        TupleValMapping =VBCX.DB.get_TupleMapping_flattened()
        resultAlph = partial_alphabet+""  # make a copy of the input
        while True:
            conclusion_happened = False
            for currPos in range(0, partial_alphabet.__len__()):
                currLetter = resultAlph[currPos]
                if currLetter != UNDEF_letter:
                    for Tuple in TupleValMapping.keys():
                        letr_A = Tuple[0]
                        letr_B = Tuple[1]
                        if currLetter == letr_A:
                            distance = TupleValMapping[Tuple]
                            otherPos = (currPos+distance) % alphLen
                            foundLetr = resultAlph[otherPos]
                            if foundLetr == UNDEF_letter:
                                conclusion_happened = True
                                # -- insert Letter into Alphabet: --
                                temp = list(resultAlph)
                                temp[otherPos] = letr_B
                                resultAlph = "".join(temp)  # re-convert to String
                                # TODO might improve performance with oldTODOlist of unchecked indexes.  (the hell did i mean by that?)
                            elif foundLetr != letr_B:
                                return "contradiction"
                        # (not needed to check the reversed case, assuming that the VCBX has been fully extrapolated (including reverse ECs).)
            if conclusion_happened == False:
                break
        return resultAlph

    # DONE, Works---
    @staticmethod
    def fill_in_undefs(partial_alphabet: str, fillerLetters: str) -> str:
        """
        Used in generate_alphabet_from_VBCX() after filling in all the defined letters.

        Fills all the places where FILLER_letter was used with one of the fillerLetters.
        """
        result = ""
        fillerLetters = list(set(fillerLetters))  # used a set for lazy randomness in the order of Letters chosen xddd
        for letter in partial_alphabet:
            if letter == UNDEF_letter:
                result += fillerLetters.pop(0)
            else:
                result += letter
        return result

    # DONE, Works---
    @staticmethod
    def GENERATE_ALPHABET_GEN10_2(possible_letters: str, alphLen: int, isomorphGroupList: list, verbose: bool) -> str:
        """
        A standalone Version of Gen10.2-generation that takes care of everything itself.
        :param isomorphGroupList [[str]] A List of Groups of Isomorphic Strings.
        :param verbose True = lotsa Printing (actually I haven't made it 100% silent yet when set to False, kinda for performance reasons. feel free to delete all prints from the Candidate-Searcher.)
        """
        if verbose:
            print("entered Gen10.2-Generation.")

        # --- PREPARATIONS: ---
        CX = CypherAnalyzer()
        for wordGroup in isomorphGroupList:
            CX.ingest_multiple_equal_words(wordGroup)
        if verbose:
            print(f"finished CX-ingestion. ({CX.DB.EC_Table.keys().__len__()} ECs)")

        # --- Candidate-search: ---
        start = timer()
        EC_Value_Assignment_dict = AlphGeneratorGen10_2.generate_working_EC_Value_Assignment(CX, alphLen)
        stopped_time = timer() - start
        if verbose:
            if EC_Value_Assignment_dict == "fail":
                print(EC_Value_Assignment_dict)
                print("Candidate-search took: ", stopped_time)
                exit()
            else:
                AlphGeneratorGen10_2.print_ECvalueMapping_invertedly(EC_Value_Assignment_dict, alphLen)
            print("Candidate-search took: ", stopped_time)
            print("------------------")
            print("------------------")
            print("------------------")
            print("------------------")

        # --- VBCX-filling ---
        VBCX = ValBasedCX(alphLen)
        TupleValAssignment = AlphGeneratorGen10_2.convert_ECvalAssignment_to_TupleValAssignment(CX, EC_Value_Assignment_dict)
        start = timer()
        AlphGeneratorGen10_2.fill_VBCX_with_TupleValAssignment(VBCX, TupleValAssignment)
        stopped_time = timer() - start
        if verbose:
            VBCX.DB.print_EC_Table_detailed()
            print("VBCX-filling took: ", stopped_time)
            print("------------------")
            print("------------------")
            print("------------------")
            print("------------------")

        # --- Alphabet-fitting ---
        relevantLetters, pointlessLetters = AlphGeneratorGen10_2.decide_relevancy_of_letters(isomorphGroupList, possible_letters)
        start = timer()
        result = AlphGeneratorGen10_2.generate_alphabet_from_VBCX(VBCX, remaining_possible_letters=relevantLetters, alphLen=alphLen, fillerLetters=pointlessLetters)
        stopped_time = timer() - start
        if verbose:
            print(f"Result={result}")
            print("Alphabet-fitting took: ", stopped_time)

        return result

