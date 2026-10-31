
def format_inr(value):
    if value is None:
        return "N/A"

    value = float(value)
    absolute_value = abs(value)

    if absolute_value >= 1_00_00_00_00_000:
        result = f"₹{value / 1_00_00_00_00_000:.2f} lakh crore"
    elif absolute_value >= 1_00_00_00_000:
        result = f"₹{value / 1_00_00_00_000:.2f} crore"
    elif absolute_value >= 1_00_000:
        result = f"₹{value / 1_00_000:.2f} lakh"
    else:
        result = f"₹{value:,.2f}"

    return result


print(format_inr(200000))
print(format_inr(20000000))
print(format_inr(2000000000))
print(format_inr(None))
