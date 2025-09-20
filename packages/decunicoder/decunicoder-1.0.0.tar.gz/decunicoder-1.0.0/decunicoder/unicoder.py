import re

def encoder(text):
    if not text:
        return ""
    
    encoded = []
    for char in text:
        code_point = ord(char)
        encoded.append(f"{code_point:05d}")
    
    return "".join(encoded)

def decoder(encoded_text):
    if not encoded_text:
        return ""
    
    if not re.match(r'^\d+$', encoded_text):
        raise ValueError("Input not Number")
    
    if len(encoded_text) % 5 != 0:
        raise ValueError("Number-string's Length is not multiple of 5")
    
    decoded_chars = []
    for i in range(0, len(encoded_text), 5):
        num_str = encoded_text[i:i+5]
        code_point = int(num_str)
        try:
            decoded_chars.append(chr(code_point))
        except ValueError:
            raise ValueError(f"Invalid Unicode Code: {code_point}")
    
    return "".join(decoded_chars)

class UnicodeConverter:
    def __init__(self):
        self.version = "1.0.0"
    
    def encode(self, text):
        return encoder(text)
    
    def decode(self, encoded_text):
        return decoder(encoded_text)
    
    def encode_file(self, input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        encoded = self.encode(content)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        return True
    
    def decode_file(self, input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            encoded = f.read()
        decoded = self.decode(encoded)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(decoded)
#
        return True
