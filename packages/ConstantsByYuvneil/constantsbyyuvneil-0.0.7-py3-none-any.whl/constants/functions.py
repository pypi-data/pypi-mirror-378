def out(x):
    print(x)

def getin(x):
    return input(x)

def Greater_among_two(x, y):
    if x>y:
        return f"{x} is greater"
    elif x==y:
        return f"{x} and {y} are equal"
    elif x<y:
        return f"{y} is greater"
    else:
        return f"Not valid values"
    
def Greatest_Among_Three(value1, value2, value3):
    if value1>value2:
        if value1>value3:
            return f"{value1} is greatest"
        elif value1<value3:
            return f"{value3} is the greatest"
        elif value1==value3:
            return f"{value1} and {value3} are equal"
    elif value1<value2:
        if value2>value3:
            return f"{value2} is the greatest"
        elif value2<value3:
            return f"{value3} is the greatest"
        elif value2==value3:
            return f"{value2} and {value3} are equal"
    elif value1==value2:
        if value1!=value3:
            return f"{value1} and {value2} are equal"
        else:
            return f"{value1}, {value2} and {value3} all are equal"
    else:
        return f"values are not valid"
        

