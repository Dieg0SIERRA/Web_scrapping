def Verify_input(input):
    # Checks whether the first or last character is a letter
    if input[0].isalpha() or input[-1].isalpha():
        if "-" in input:
            output = input.replace("-", "").upper()
        elif "/" in input:
            output = input.replace("/", "").upper()
        else:
            raise ValueError("Invalid pair format. Use btc-usdt or btc/usdt format.")
    return output