import os

filepath = r"c:\Users\mahes\OneDrive\Desktop\Projects\Projects_Personal\Niyati\frontend\src\app\upload\page.tsx"

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Encode as windows-1252 to get the original bytes back, then decode as utf-8
try:
    corrected = text.encode('windows-1252').decode('utf-8')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(corrected)
    print("Fixed encoding successfully!")
except Exception as e:
    # If the exact windows-1252 -> utf-8 mapping fails, we might just be dealing with regular copy-paste garbled text
    print(f"Failed strict decode: {e}")
    # Let's try latin1
    try:
        corrected = text.encode('latin1').decode('utf-8')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(corrected)
        print("Fixed encoding via Latin1 successfully!")
    except Exception as e2:
        print(f"Failed Latin1 too: {e2}")
