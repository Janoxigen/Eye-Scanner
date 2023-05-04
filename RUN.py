

###########################################################
"""
CD: 04.05.2023
"""
###########################################################


# ---------------------------------------
# --------------- IMPORTS ---------------
# ---------------------------------------
from timeit import default_timer as timer  # to measure exec time
from theBackrooms.Isomorph_Searcher import Isomorph_Searcher as IsoScanner
from theBackrooms.AlphGeneratorGen10_2 import AlphGeneratorGen10_2 as AG10_2




# -------------------------------------------------------
# -------- PREPARATION (for Alphabet-generation) --------
# -------------------------------------------------------
alphLen = 83
possible_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqr_;>@^)!<$(\\:%&',#=\" -.+/]`?[*"
isomorphs = [
    [
        "535OP3PO3",  # Messages 1-3,  first Triple, including the left extension, ONLY LYMM-PAIRS
        "HQH&`Q`&Q",
    ],
    [
        "OP3PO3",  # Messages 1-3,  the common Parts of the sextuple, ONLY LYMM-PAIRS
        "&`Q`&Q",
        "gj$jg$",
        "d1-1d-",
        "IY7YI7",
    ],
    [
        ":OLP3PO3L:",  # Messages 2-3,  the sextuples including the blue-black long Lymm-Pairs, ONLY LYMM-PAIRS
        "0&-`Q`&Q-0",
        "cdN1-1d-Nc",
        "JIhY7YI7hJ",
    ],
    [
        ":OLP3PO3L:``",  # Message 2,  the right-extension of the two sextuples including the blue-black long Lymm-Pairs, ONLY LYMM-PAIRS
        "cdN1-1d-Nc^^",
    ],
    [
        "0&-`Q`&Q-0**",  # Message 3,  the right-extension of the two sextuples including the blue-black long Lymm-Pairs, ONLY LYMM-PAIRS
        "JIhY7YI7hJ%%",
    ],
    [
        "W,,W",  # Messages 4-6,  the longass Isomorphs, ONLY LYMM-PAIRS
        "[--[",
        "@33@",
    ],
    [
        "OMdMOd",  # Messages 7-9,  the dense Isomorphs, ONLY LYMM-PAIRS
        "RYgYRg",
        "'B>B'>",
    ],
    [
        "H::H",  # Messages 7-9,  the greenbrown Isomorphs, ONLY LYMM-PAIRS
        "c55c",
        "5ii5",
    ],
]
example_extension = [
    # (you can use "°" for Columns that are not part of the Isomorph.)
    [
        "OM°deo9FM°Od",  # Messages 7-9,  dense Isomorph, including all the middle Gap-Letters
        "RY°gk:dVY°Rg",
        "'B°>?3:(B°'>",
    ],
    # (you can prepend "r" to make python ignore the backslashes)
    [
        r"W]O,5,°°°°°°°W",  # Messages 4-6,  longass Isomorph, including first half of all the Gap-Letters
        r"[Ip-\-°°°°°°°[",
        r"@+23K3°°°°°°°@",
    ]
]

isomorphs.extend(example_extension)



# -----------------------------------------------
# ------------- ALPHABET-GENERATION -------------
# -----------------------------------------------
start = timer()  # for testprints
alphabet = AG10_2.GENERATE_ALPHABET_GEN10_2(possible_letters, alphLen, isomorphs, verbose=True)
stopped_time = timer() - start  # for testprints

# (alternatively, you could also provide a hardcoded Alphabet like this)
#alphabet = "5*lY_BaW%#MZ;CSAH!qT<4U K\\8,G6.@[i=nLNXRg'>D]$OdE:c3-k9?ojrhem&P10fQ+I2pJ)7V\"(/`^bF"

print(f"Result={alphabet}")                         # testprint
print("Alphabet-generation took: ", stopped_time)   # testprint



# -----------------------------------------------------
# -------- PREPARATION (for Isomorph-Scanning) --------
# -----------------------------------------------------
relLttrs, flLttrs = AG10_2.decide_relevancy_of_letters(isomorphs, alphabet)
f = open("input\CYPHERTEXT.txt", "r")  # (the File needs to be in this Project in a [input\IsoScanner_Input] folder)
cyphertext = f.read()
lines = cyphertext.split("\n")
ISX = IsoScanner(alphabet)
# IMPORTANT: YOU CAN CUSTOMIZE the decision of "what is an Isomorph" in the check_mask_for_Isos() Function of that Class.
# IMPORTANT: YOU CAN CUSTOMIZE the colors that are used for Marking Isomorphs in the print_messages_marked() Function of that Class.



# -----------------------------------------------
# ------------- ISOMORPHS-SCANNING -------------
# -----------------------------------------------
ISX.Eyenalisis(lines, 0,1,2, relLttrs, flLttrs)
ISX.Eyenalisis(lines, 3,4,5, relLttrs, flLttrs)
ISX.Eyenalisis(lines, 6,7,8, relLttrs, flLttrs)