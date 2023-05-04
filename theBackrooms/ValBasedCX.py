
from theBackrooms.MDA_Database import MDA_Database


class conflicting_ECs_Exception(Exception):
    """
    Raised if a function detects some contradiction in the ECs.
    """
    pass  # (this class needs no content)

class ValBasedCX:
    """
    This is a value-based CX that uses specific Values as EC-IDs instead of meaningless strings.

    Given the Value-Basedness:
        >EC-merging isn't needed cuz we always already know if Tuples are in the same EC.
        >EC-Rotation only works if two of the three involved ECs have a Value assigned to them.
    """
    # DONE, Works---
    def __init__(self, alphLen: int):
        self.alphLen = alphLen
        self.DB = MDA_Database()
        for EC_id in range(0, alphLen):
            self.DB.create_empty_EC(EC_id)  # (ignore the warning, I will be using INTs in this class.)

    # DONE, Works---
    def ingest_new_Tuple_Assignment(self, Tuple: tuple, Value: int) -> str:
        """
        Puts the Tuple into the given Value's EC, and does CONFLICT-CHECKING, but nothing more.
        Automatically also inserts the reversed Tuple into the reversed EC.
        (Tuple-Extrapolations are still needed though.)
        :returns: "Tuple already in given EC" or "CONFLICTING TUPLES" or "assignment successful".
        """
        DB = self.DB
        tuple_exists = DB.check_if_Tuple_exists(Tuple)

        # --- if the Tuple already has an EC: ---
        if tuple_exists:
            # Check if it is in the Correct Value:
            found_EC = DB.get_EC_of_Tuple(Tuple)
            if found_EC == Value:
                return "Tuple already in given EC"  # terminate if yes.

        # --- if the Tuple is new: ---
        DB.set_Tuple_EC(Tuple, Value)  # (ignore the string-warning)
        reversed_Tuple = (Tuple[1], Tuple[0])
        reversed_Value = (-Value) % self.alphLen
        DB.set_Tuple_EC(reversed_Tuple, reversed_Value)  # (ignore the string-warning)

        # --- conflict-checking: ---
        # (no need for reversed conflict-checking, cuz i assume that that is just the mirrored EC.)
        Tuplelist = DB.get_Tuples_of_EC(Value)  # (ignore the string-warning)
        conflict = self.__conflict_check_EC(Tuplelist)
        if conflict is True:
            return "CONFLICTING TUPLES"
        return "assignment successful"

    # DONE, Works---
    def extrapolate_all_Tuples(self):
        """
        Extrapolates all the possible conclusions that can be drawn from pairs of known Tuples.
        (Changes the Currstate, adding all new Tuples to the DB)
        """
        TODOlist = set(self.DB.get_global_TupleList())
        while True:  # until the T0DO-List is empty
            if TODOlist.__len__()==0:
                break
            Tuple_A = TODOlist.pop()
            letr_A1 = Tuple_A[0]
            letr_A2 = Tuple_A[1]
            ECval_A = self.DB.get_EC_of_Tuple(Tuple_A)
            allTuples = list(self.DB.get_global_TupleList())  # (takes a snapshot of the current DB-state)
            # ---- for all pairings with other Tuples: ----
            for Tuple_B in allTuples:
                if Tuple_A==Tuple_B:
                    continue
                letr_B1 = Tuple_B[0]
                letr_B2 = Tuple_B[1]
                ECval_B = self.DB.get_EC_of_Tuple(Tuple_B)
                # ---- do extrapolation: ----
                # (no need to take care of the reversed ECs, since Tuple-Assignment already does that AND the reversed Tuples will do that too.)
                conclusions = []  # a List of Tuples   Tuple->ECval
                # -- if A+B form a chain like XY,YZ --
                if letr_A2==letr_B1:
                    ECval_XZ = ECval_A + ECval_B
                    ECval_XZ = ECval_XZ % self.alphLen
                    Tuple_XZ = (letr_A1, letr_B2)
                    if ECval_XZ != 0:
                        conclusions.append((Tuple_XZ, ECval_XZ))
                        #print(f"{letr_A1}{letr_A2}+{letr_B1}{letr_B2}={Tuple_XZ[0]}{Tuple_XZ[1]}")  # testprint
                # -- if B+A form a chain like ZY,YX -- (aka inverted)
                if letr_B2==letr_A1:
                    ECval_ZX = ECval_B + ECval_A
                    ECval_ZX = ECval_ZX % self.alphLen
                    Tuple_ZX = (letr_B1, letr_A2)
                    if ECval_ZX != 0:
                        conclusions.append((Tuple_ZX, ECval_ZX))
                        #print(f"{letr_A1}{letr_A2}+{letr_B1}{letr_B2}={Tuple_ZX[0]}{Tuple_ZX[1]}")  # testprint
                # -- if A+B form a chain like XY,XZ -- (aka same anker)
                if letr_A1==letr_B1:
                    ECval_YZ = ECval_B - ECval_A  # (ignore the string-warning)
                    ECval_YZ = ECval_YZ % self.alphLen
                    Tuple_YZ = (letr_A2, letr_B2)
                    if ECval_YZ != 0:
                        conclusions.append((Tuple_YZ, ECval_YZ))
                        #print(f"{letr_A1}{letr_A2}+{letr_B1}{letr_B2}={Tuple_YZ[0]}{Tuple_YZ[1]}")  # testprint
                # -- if A+B form a chain like XY,ZY -- (aka same result)
                if letr_A2==letr_B2:
                    ECval_XZ = ECval_A - ECval_B  # (ignore the string-warning)
                    ECval_XZ = ECval_XZ % self.alphLen
                    Tuple_XZ = (letr_A1, letr_B1)
                    if ECval_XZ != 0:
                        conclusions.append((Tuple_XZ, ECval_XZ))
                        #print(f"{letr_A1}{letr_A2}+{letr_B1}{letr_B2}={Tuple_XZ[0]}{Tuple_XZ[1]}")  # testprint

                # -- insert all the conclusions into the DB --
                for conclusion in conclusions:
                    Tuple = conclusion[0]
                    Value = conclusion[1]
                    currValue = self.DB.get_EC_of_Tuple(Tuple)
                    if currValue == None:
                        #print(f"{Tuple[0]}{Tuple[1]}={Value}")  # testprint
                        self.ingest_new_Tuple_Assignment(Tuple, Value)  # (ignore the string-warning)
                        TODOlist.add(Tuple)
                    else:  # if the Tuple already has an EC
                        #print(f"{Tuple[0]}{Tuple[1]}={currValue}->{Value}")  # testprint
                        if currValue != Value:
                            raise conflicting_ECs_Exception()

    # DONE, Works---
    @staticmethod
    def __conflict_check_EC(TupleList: list) -> bool:
        """
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

