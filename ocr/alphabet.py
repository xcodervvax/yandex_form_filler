ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"

char2idx = {char: idx for idx, char in enumerate(ALPHABET)}
idx2char = {idx: char for idx, char in enumerate(ALPHABET)}

NUM_CLASSES = len(ALPHABET)