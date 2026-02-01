import re
import sys
import math
import os

# Grid Mapping
# We define a visual grid of 18 columns.
# Cols 0-5: Left Hand Fingers
# Cols 6-8: Left Hand Thumb (Offset)
# Cols 9-11: Right Hand Thumb (Offset)
# Cols 12-17: Right Hand Fingers

# Map the keyboard's visual grid to the key indices.
# An example of the visual grid:
# |  F1   |  F2 |  F3 |  F4  |  F5  |                                                               |  F6   |  F7   |  F8  |   F9  |  F10 |
# |  =    |  1  |  2  |  3   |  4   |  5   |                                                 |  6   |   7   |   8   |  9   |   0   |   -  |
# |  TAB  |  Q  |  W  |  E   |  R   |  T   |                                                 |  Y   |   U   |   I   |  O   |   P   |   \  |
# |  ESC  |  A  |  S  |  D   |  F   |  G   |                                                 |  H   |   J   |   K   |  L   |   ;   |   '  |
# |   `   |  Z  |  X  |  C   |  D   |  V   | LSHFT | LCTRL | LOWER | | LGUI  | RCTRL | RSHFT |  N   |   M   |   ,   |  .   |   /   | PGUP |
# | MAGIC | HOME| END | LEFT | RIGHT|      | BSPC  | DEL   | LALT  | | RALT  | RET   | SPACE |      |  UP   | DOWN  |  [   |   ]   | PGDN |

ROW_MAPPINGS = [
    # Row 0: F1-F10. 
    # L: 0-4 -> Cols 0-4
    # Col 5 is empty
    # Thumb columns (6-11) are empty (Offset by 6 from the start of the row)
    # Col 12 is empty
    # R: 5-9 -> Cols 13-17 (Col 12 Empty) - Assuming symmetry with Row 1
    {
        0: 0, 1: 1, 2: 2, 3: 3, 4: 4,  # Left
        5: 13, 6: 14, 7: 15, 8: 16, 9: 17 # Right
    },
    
    # Row 1: 12 keys (10-21). Cols 0-5 and 12-17.
    {
        10: 0, 11: 1, 12: 2, 13: 3, 14: 4, 15: 5,
        16: 12, 17: 13, 18: 14, 19: 15, 20: 16, 21: 17
    },
    
    # Row 2: 12 keys (22-33). Same as Row 1.
    {
        22: 0, 23: 1, 24: 2, 25: 3, 26: 4, 27: 5,
        28: 12, 29: 13, 30: 14, 31: 15, 32: 16, 33: 17
    },

    # Row 3: 12 keys (34-45). Same as Row 1.
    {
        34: 0, 35: 1, 36: 2, 37: 3, 38: 4, 39: 5,
        40: 12, 41: 13, 42: 14, 43: 15, 44: 16, 45: 17
    },

    # Row 4: 18 keys (46-63).
    # L Fingers: 46-51 (6 keys) -> Cols 0-5.
    # L Thumb: 52-54 (3 keys) -> Cols 6-8.
    # R Thumb: 55-57 (3 keys) -> Cols 9-11.
    # R Fingers: 58-63 (6 keys) -> Cols 12-17.
    {
        46: 0, 47: 1, 48: 2, 49: 3, 50: 4, 51: 5,
        52: 6, 53: 7, 54: 8,
        55: 9, 56: 10, 57: 11,
        58: 12, 59: 13, 60: 14, 61: 15, 62: 16, 63: 17
    },

    # Row 5: 16 keys (64-79).
    # L Fingers: 64-68 (5 keys) -> Cols 0-4. Col 5 Empty.
    # L Thumb: 69-71 (3 keys) -> Cols 6-8.
    # R Thumb: 72-74 (3 keys) -> Cols 9-11.
    # R Fingers: 75-79 (5 keys) -> Cols 13-17. Col 12 Empty (inner).
    {
        64: 0, 65: 1, 66: 2, 67: 3, 68: 4, # Col 5 empty (index 5 visually)
        69: 6, 70: 7, 71: 8,
        72: 9, 73: 10, 74: 11,
        75: 13, 76: 14, 77: 15, 78: 16, 79: 17 # Col 12 empty
    }
]

def format_layer(bindings):
    # Flatten bindings (remove newlines/tabs and split)
    # Be careful to split by whitespace but keep '&kp N1' together
    # Actually, the input bindings are likely just a list of strings if we parse correctly.
    # Or raw text.
    
    # Simple parser: split by & and rejoin
    key_codes = ['&' + b.strip() for b in bindings.replace('\n', ' ').replace('\t', ' ').split('&') if b.strip()]

    if len(key_codes) != 80:
        raise ValueError(f"Layer with bindings {bindings} has {len(key_codes)} keys, expected 80.")
    
    grid = [[""] * 18 for _ in range(6)] # 6 Rows
    for row_idx, mapping in enumerate(ROW_MAPPINGS):
        # Populate columns
        for key_idx, col_idx in mapping.items():
            if key_idx < 0 or key_idx >= len(key_codes):
                raise ValueError(f"Mapping error: key index {key_idx} is out of range")

            grid[row_idx][col_idx] = key_codes[key_idx]
    
    # Make spacing in each column consistent
    for col_idx in range(18):
        col_keys = [grid[row_idx][col_idx] for row_idx in range(6)]

        # Minimum 2 spaces padding
        col_width = max(len(key) for key in col_keys) + 2

        for row_idx in range(6):
            grid[row_idx][col_idx] = grid[row_idx][col_idx].ljust(col_width)
    
    # Final adjustments
    for row_idx in range(6):
        # Add 4 spaces to the middle column (Col 9)
        grid[row_idx][9] += " " * 4

        # Indent the line
        grid[row_idx][0] = " " * 8 + grid[row_idx][0]

    return "\n".join(["".join(row) for row in grid])

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # First, find the keymap block to only process bindings within it
    # The keymap block starts with "keymap {" and we need to find its matching closing brace
    keymap_match = re.search(r'keymap\s*\{', content)
    if not keymap_match:
        raise ValueError("Could not find keymap block in file")
    
    keymap_start = keymap_match.start()
    
    # Find the matching closing brace for the keymap block
    # Count braces to find the correct closing brace
    brace_count = 0
    keymap_end = None
    for i in range(keymap_match.end() - 1, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                keymap_end = i + 1
                break
    
    if keymap_end is None:
        raise ValueError("Could not find end of keymap block")
    
    # Extract parts: before keymap, keymap content, after keymap
    before_keymap = content[:keymap_start]
    keymap_content = content[keymap_start:keymap_end]
    after_keymap = content[keymap_end:]

    # Find all bindings = < ... >; blocks within the keymap section only
    # We use a regex that captures the content inside < ... >
    # Handles multi-line
    pattern = re.compile(r'(bindings\s*=\s*<)([^>]+)(>;)', re.DOTALL)
    
    def replacer(match):
        prefix = match.group(1)
        bindings_text = match.group(2)
        suffix = match.group(3)
        
        formatted = format_layer(bindings_text)
        if formatted:
            return f"{prefix}\n{formatted}\n        {suffix}"
        else:
            return match.group(0) # Return original if failed

    # Only apply replacement to the keymap content
    new_keymap_content = pattern.sub(replacer, keymap_content)
    
    # Reconstruct the file
    new_content = before_keymap + new_keymap_content + after_keymap
    
    with open(filepath, 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        if os.path.exists(r"./config/glove80.keymap"):
            filepath = r"./config/glove80.keymap"
        else:
            raise ValueError("No keymap file provided and ./config/glove80.keymap does not exist")
    else:
        for filepath in sys.argv[1:]:
            process_file(filepath)
