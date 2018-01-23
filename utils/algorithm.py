# Return count numbers after comma in float
# Max count numbers after comma = 12
def count_after_dot(number: float) -> int:
    s = "{:.12f}".format(number)
    for c in reversed(s):
        if c == '0':
            s = s[:len(s)-1]
        if c != '0':
            break
    if '.' in s:
        fd = s.find('.')
        count = abs(s.find('.') - len(s)) - 1
        if count == 1 and s[fd + 1] == '0':
            return 0
        return count
    else:
        return 0

def reduce_to_step_size(num: float, step: float) -> float:
    div = num / step
    s = str(div)
    exponent = s[:s.find(".")]
    return round(float(exponent) * step, 16)

if __name__ == "__main__":
    """c = count_after_dot(0.001)
    total = 0.036963
    quantity = round(total, c)
    if total < quantity:
        print("error")
    print(quantity)

    a = 192.0
    print(f"{a:.12f}")"""

print(reduce_to_step_size(0.036963, 0.0001))
