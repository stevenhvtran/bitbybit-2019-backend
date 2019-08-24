def wordcount(text):
    if text == '':
        return 0
    else:
        SplitText = text.split(' ')
        return len(SplitText)


def timer(compare_number):
    if compare_number >= 56:
        return 'High productivity'
    elif compare_number >= 46 and compare_number < 56:
        return 'Mid productivity'
    elif compare_number > 0:
        return 'Low productivity'
    elif compare_number == 0:
        return 'No productivity'
    else:
        return 'Error'


def compare_strings(string_one, string_two):
    def get_words(s):
        d = {}
        words = s.split(" ")
        for word in words:
            if word in d:
                d[word] += 1
            else:
                d[word] = 1
        return d

    dict_one = get_words(string_one)
    dict_two = get_words(string_two)

    keys = set().union(dict_one.keys(), dict_two.keys())
    progress = 0
    for key in keys:
        if key in dict_one and key in dict_two:
            progress += abs(dict_one[key] - dict_two[key])
        elif key in dict_two:
            progress += dict_two[key]
    return progress


def app():
    prev = ""
    while True:
        new = input("enter string: ")
        if new.lower() == "q":
            break
        compare_value = compare_strings(prev, new)
        print("progress:", compare_value)
        print(f'productivity: {timer(compare_value)}')
        prev = new

print("imported scratch.py")

if __name__ == '__main__':
    app()

