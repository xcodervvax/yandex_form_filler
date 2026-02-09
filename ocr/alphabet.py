ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"

# CTC: 0 зарезервирован под blank
char2idx = {char: idx + 1 for idx, char in enumerate(ALPHABET)}
idx2char = {idx + 1: char for idx, char in enumerate(ALPHABET)}

BLANK_IDX = 0
NUM_CLASSES = len(ALPHABET) + 1
