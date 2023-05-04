

from colorama import Fore, Back, Style

import numpy as np

class Isomorph_Searcher:
    """
    This class allows for automated discovery of (prominent) Isomorphs when given a CypherAlphabet.
    For now, it is limited to finding triplet-Isomorphs between three messages (each message one Isomorph-instance).
    But maybe I'll also implement two-message-Isomorphs.
    (By inputting one message twice (or thrice) instead of three distinct messages, you can do two-message scanning (and one message scanning))

    IMPORTANT: YOU CAN CUSTOMIZE the decision of "what is an Isomorph" in the check_mask_for_Isos() Function.
    IMPORTANT: YOU CAN CUSTOMIZE the colors that are used for Marking Isomorphs in the print_messages_marked() Function.
    """

    # DONE, Works---
    def __init__(self, Alphabet: str, max_isomorph_offset=50):
        self.Alphabet = Isomorph_Searcher.convert_AlphabetString_to_ValueDict(Alphabet)
        self.Alph_size = Alphabet.__len__()
        self.max_isomorph_offset = max_isomorph_offset

    # DONE, Works---
    def set_alphabet(self, Alphabet: str):
        self.Alphabet = Isomorph_Searcher.convert_AlphabetString_to_ValueDict(Alphabet)
        self.Alph_size = Alphabet.__len__()

    # DONE, Works---
    def convert_message_to_ValueList(self, message: str) -> np.ndarray:
        """
        :returns: A numpy-Array that matches the numerical Values of the given message under the given C-Alph.
        """
        message_length = message.__len__()
        result = np.zeros(shape=message_length, dtype=int)
        for currpos in range(0, message_length):
            result[currpos]=self.Alphabet[message[currpos]]
        return result

    # DONE, Works---
    @staticmethod
    def convert_AlphabetString_to_ValueDict(Alphabet_String: str) -> dict:
        """
        :returns: A Dict that lists for every letter (of the given C-Alp) which position it occurred in.
        """
        dictionary = {}
        for i in range(0, Alphabet_String.__len__()):
            dictionary[Alphabet_String[i]] = i
        return dictionary

    # DONE, Works---
    @staticmethod
    def truncate_to_same_length(A,B,C):
        """
        Returns truncated Versions of the given List-like Inputs, up to the size of the smaller one.
        """
        size = min(A.__len__(), B.__len__(), C.__len__())
        A_trunced = A[:size]
        B_trunced = B[:size]
        C_trunced = C[:size]
        return (A_trunced, B_trunced, C_trunced)

    # DONE, Works--- (unused, cuz that single line can also be used manually)
    def deltalize_two_messages(self, msg_A: np.ndarray, msg_B: np.ndarray) -> np.ndarray:
        """
        ONLY works when both messages are the same size!

        Delta= (A-B)%alph
        :returns: An Array that contains all the Deltas between aligned Indexes in both Input-Arrays.
        """
        return (msg_A - msg_B) % self.Alph_size

    # DONE, Works---
    def analyze_message_triplets(self, msg_A_str, msg_B_str, msg_C_str, printMasks=True):
        """
        This is the main Analyzer-Function.
        It goes over all the possible combinations of Offsettings between the three Messages.
        For now, it only prints the resulting alignment, but later:
        It generates the Isomorph-Mask for each Triple of aligned Values for each such Offsetting.
        Later, those masks can be filtered to only keep those that containg prominent Isomorphs.
        (Assumes that all messages are at least 20 Chars long)
        Note: the way this is writen rn, it can take either strings or Lists as messages.
                (Strings only if only_testprints=True)
        """

        msg_A = self.convert_message_to_ValueList(msg_A_str)
        msg_B = self.convert_message_to_ValueList(msg_B_str)
        msg_C = self.convert_message_to_ValueList(msg_C_str)

        found_Isomorphs = []  # this list will be where i put the Isomorph-masks that I find suspicious
        max_iso_offset = self.max_isomorph_offset
        for wanted_offset_B in range(-max_iso_offset, max_iso_offset):
            for wanted_offset_C in range(-max_iso_offset, max_iso_offset):
                if abs(wanted_offset_B - wanted_offset_C) > max_iso_offset:
                    continue  # (this skip is just to minimize the amount of HUUUGE offsettings that are tested.)
                # -- shift the offsets so that none of them are negative: --
                shift = -min(0, wanted_offset_B, wanted_offset_C)  # do a correcting shift only if B or C would be smaller than 0
                offset_A = shift
                offset_B = wanted_offset_B + shift
                offset_C = wanted_offset_C + shift
                # -- slice the messages according to the offsets: --
                realigned_A_msg = msg_A[offset_A:]
                realigned_B_msg = msg_B[offset_B:]
                realigned_C_msg = msg_C[offset_C:]
                A,B,C = self.truncate_to_same_length(realigned_A_msg, realigned_B_msg, realigned_C_msg)
                # -- generate the two Delta-Streams AB and AC: --
                delt_AB = (B - A) % self.Alph_size
                delt_AC = (C - A) % self.Alph_size
                delt_BC = (C - B) % self.Alph_size
                masklength = A.__len__()
                # -- For each aligned Triple of Values: --
                seen_sus_delta_combos = []
                for i in range(0, masklength):
                    # -- Generate the Iso-Mask: --
                    AB_val = delt_AB[i]
                    AC_val = delt_AC[i]
                    BC_val = delt_BC[i]
                    if (AB_val==0) or (AC_val==0) or (BC_val==0):  # skip all triples where two cypherletters where the same (ergo delta=0)
                        # TODO YOU CAN CHANGE THIS to "continue" if you want to throw away all isomorphs that aren't made up of three totally different Strings.
                        pass
                        #continue
                    mask_AB = delt_AB==AB_val  # create a Mask showing TRUE wherever AB_val occurs in AB.
                    mask_AC = delt_AC==AC_val  # create a Mask showing TRUE wherever AC_val occurs in AC.
                    combined_mask = mask_AB & mask_AC
                    # -- analyze the Mask for suspicious Patterns: --
                    is_sussy = self.check_mask_for_Isos(combined_mask)

                    if is_sussy:
                        delta_combo = (AB_val,AC_val)
                        if delta_combo not in seen_sus_delta_combos:
                            description = {"A_offset":offset_A,
                                           "B_offset":offset_B,
                                           "C_offset":offset_C,
                                           "AB_val":AB_val,
                                           "AC_val":AC_val,
                                           "BC_val":BC_val,
                                           "mask":combined_mask}
                            found_Isomorphs.append(description)
                            seen_sus_delta_combos.append(delta_combo)
        if printMasks:
            for description in found_Isomorphs:
                self.print_triplet_mask_marked(msg_A_str, msg_B_str, msg_C_str, description)
        return found_Isomorphs

    # DONE, Works---  (unused but useful for examination of specific Isomorphs.)
    def analyze_specific_setup(self,
                               msg_A_str,
                               msg_B_str,
                               msg_C_str,
                               offset_A: int,
                               offset_B: int,
                               offset_C: int,
                               position=-1,
                               printMasks=True):
        """
         Does a Single Iteration of the analyze_message_triplets(), with the given Offsets.
         If the triple-position isn't specified, it scans all the triplets on that offseting.
        """

        msg_A = self.convert_message_to_ValueList(msg_A_str)
        msg_B = self.convert_message_to_ValueList(msg_B_str)
        msg_C = self.convert_message_to_ValueList(msg_C_str)
        found_Isomorphs = []  # this list will be where i put the Isomorph-masks that I find suspicious

        # -- slice the messages according to the offsets: --
        realigned_A_msg = msg_A[offset_A:]
        realigned_B_msg = msg_B[offset_B:]
        realigned_C_msg = msg_C[offset_C:]
        A,B,C = self.truncate_to_same_length(realigned_A_msg, realigned_B_msg, realigned_C_msg)
        # -- generate the two Delta-Streams AB and AC: --
        delt_AB = (B - A) % self.Alph_size
        delt_AC = (C - A) % self.Alph_size
        delt_BC = (C - B) % self.Alph_size
        masklength = A.__len__()
        # -- For each aligned Triple of Values: --  (or the one specific one that was requested)
        choices = [position]
        if position == -1:
            choices = range(0, masklength)

        seen_sus_delta_combos = []
        for i in choices:
            # -- Generate the Iso-Mask: --
            AB_val = delt_AB[i]
            AC_val = delt_AC[i]
            BC_val = delt_BC[i]
            if (AB_val==0) or (AC_val==0) or (BC_val==0):  # skip all triples where two cypherletters where the same (ergo delta=0)
                # TODO YOU CAN CHANGE THIS to "continue" if you want to throw away all isomorphs that aren't made up of three totally different Strings.
                pass
                #continue
            mask_AB = delt_AB==AB_val  # create a Mask showing TRUE wherever AB_val occurs in AB.
            mask_AC = delt_AC==AC_val  # create a Mask showing TRUE wherever AC_val occurs in AC.
            combined_mask = mask_AB & mask_AC
            # -- analyze the Mask for suspicious Patterns: --
            is_sussy = self.check_mask_for_Isos(combined_mask)

            if is_sussy:
                delta_combo = (AB_val,AC_val)
                if delta_combo not in seen_sus_delta_combos:
                    description = {"A_offset":offset_A,
                                   "B_offset":offset_B,
                                   "C_offset":offset_C,
                                   "AB_val":AB_val,
                                   "AC_val":AC_val,
                                   "BC_val":BC_val,
                                   "mask":combined_mask}
                    found_Isomorphs.append(description)
                    seen_sus_delta_combos.append(delta_combo)
        if printMasks:
            for description in found_Isomorphs:
                self.print_triplet_mask_marked(msg_A_str, msg_B_str, msg_C_str, description)
        return found_Isomorphs


    # DONE, Works---
    @staticmethod
    def check_mask_for_Isos(mask: np.ndarray) -> bool:
        """
        Looks at the Patterns of a given Mask and returns TRUE if it might be an isomorph.
        For now, it just checks if the number of set Flags is high enough, regardless of distribution or pattern.
        """
        return mask.sum() >= 4

    # DONE, Works---
    @staticmethod
    def print_triplet_mask_marked(msg_A_str: str, msg_B_str: str, msg_C_str: str,
                                  description: dict, relevantLetters="a", fillerLetters="b"):
        """
        When given a mask-describing Dict, it prints the given three messages and marks the masked places while printing.
        Descriptio-Dicts look like this:
               "A_offset":offset_A,
               "B_offset":offset_B,
               "C_offset":offset_C,
               "AB_val":AB_val,
               "AC_val":AC_val,
               "BC_val":BC_val,
               "mask":combined_mask}
        :param relevantLetters is an alphabet-string that contains all the Letters that have been defined by Isomorphs.
        :param fillerLetters is an alphabet-string that contains all the  filler-Letters (not in any Isomorph).
        """

        datasets = []
        AB_val = description["AB_val"]
        AC_val = description["AC_val"]
        msg_A_entry = {"messageNameString":"A",
                       "messageString":msg_A_str,
                       "messageLength":msg_A_str.__len__(),
                       "offset":description["A_offset"],
                       "mask":description["mask"],
                       "suffixString":""
                       }
        msg_B_entry = {"messageNameString":"B",
                       "messageString":msg_B_str,
                       "messageLength":msg_B_str.__len__(),
                       "offset":description["B_offset"],
                       "mask":description["mask"],
                       "suffixString":f"      AB={AB_val}"
                       }
        msg_C_entry = {"messageNameString":"C",
                       "messageString":msg_C_str,
                       "messageLength":msg_C_str.__len__(),
                       "offset":description["C_offset"],
                       "mask":description["mask"],
                       "suffixString":f"      AC={AC_val}"
                       }
        datasets.append(msg_A_entry)
        datasets.append(msg_B_entry)
        datasets.append(msg_C_entry)

        Isomorph_Searcher.print_messages_marked(datasets, relevantLetters, fillerLetters)

    # DONE, Works---
    @staticmethod
    def print_messages_marked(datasets: list, relevantLetters="a", fillerLetters="b"):
        """
        A flexible Version of the triplet-printer.
        The Dataset-LIST describes for each Message with a DICT how it is to be printed:
            >messageNameString
            >messageString
            >messageLength
            >offset
            >mask (unpadded)  (a numpy INT-List)
            >suffixString (used for the DeltaValues like  "AB=12")
        """
        # -- LetterColoring-Implementation: --

        # (I have to use two different Modes because IntelliJ somehow fucks the colorscheme up in each
        # mode and there is no setting that works in both colorModes.)
        #NightMode = True
        NightMode = False
        if NightMode:
            MarkCOLOR = Back.GREEN
            relevantCOLOR = ""
            fillerCOLOR = Fore.LIGHTRED_EX  # no idea why RED, LIGHTRED and BLUE cause the marking-background to be lighter...
            RESET_ALL = Back.RESET + Fore.RESET
        else:  # DAYMODE:
            MarkCOLOR = Back.LIGHTGREEN_EX
            relevantCOLOR = ""
            fillerCOLOR = Fore.RED
            RESET_ALL = Back.RESET + Fore.RESET

        # ---- PRINT INTRODUCTION LINE ----
        output = ""
        for dataset in datasets:
            msg_name = dataset["messageNameString"]
            offset = dataset["offset"]
            output += f"{msg_name}={offset}, "
        print(output)

        # ---- PRINT MARKED MESSAGES ----
        for dataset in datasets:
            # -- prepare all the Variables --
            msg_str = dataset["messageString"]
            msg_len = dataset["messageLength"]
            offset = dataset["offset"]
            mask = dataset["mask"]
            suffixString = dataset["suffixString"]
            mask_len = mask.__len__()

            # -- add padding to the Mask to make it the same size as the strings (and correct offset.) --
            mask_aligned = np.concatenate((np.zeros(offset), mask, np.zeros( msg_len-(offset+mask_len) )), axis=None)

            # -- print te message, with coloring wherever mask=True --
            for i in range(0,msg_len):
                currLetter = msg_str[i]
                output = currLetter
                if mask_aligned[i] == True:
                    output = MarkCOLOR + output
                if currLetter in fillerLetters:
                    output = fillerCOLOR + output
                if currLetter in relevantLetters:
                    output = relevantCOLOR + output
                print(output+RESET_ALL, end="")
            print(suffixString)

    # DONE, Works---
    def Eyenalisis(self,
                   lines: list,
                   index_A: int,
                   index_B: int,
                   index_C: int,
                   relevantLetters: str,
                   fillerLetters: str):
        """
        Runs Eye-Isoscanning on the three chosen Lines and prints the marked Results.
        The User specifies which EyeMessages are scanned using the "index"-Variables.
        :param lines a List of the Input-Strings (each Eye-Message).
        """
        result = self.analyze_message_triplets(lines[index_A], lines[index_B], lines[index_C], printMasks=False)
        for description in result:
            self.print_triplet_mask_marked(lines[index_A], lines[index_B], lines[index_C], description, relevantLetters,
                                          fillerLetters)
        print("------------------------------------")