def create_dict_from_file(filename):
    keys = []
    values = []
    try:
        with open(filename) as f:
            for line in f:
                text = line.strip()
                fields = text.split(",")
                keys.append(fields[0])
                values.append(int(fields[1]))

    except:
        print("not found")

    dictionary = {k: v for k, v in zip(keys, values)}
    return dictionary


def dict_to_file(my_dict, filename):
    with open(filename, "w", encoding="utf-8") as file:
        for key, value in my_dict.items():
            file.write(f"{key},{value}\n")


def print_dict(dictionary):
    count = 1
    for key, value in dictionary.items():
        print(f"{count}- {key},{value}")
        count += 1


def isNumber(s):
    return s.isdigit()


def dictionary_by_index(my_dict, index):
    keys = list(my_dict.keys())
    return keys[index]


def validate_add(product_input, my_dict):
    if isNumber(product_input):
        product_input = int(product_input)
        numbers = list(range(1, len(my_dict) + 1))

        if product_input in numbers:
            return 1
        else:
            print("\nselect suitable number to proceed or an item's name")
            return -1

    elif product_input in my_dict:
        return 2

    else:
        return 3


my_dict = create_dict_from_file("stock.txt")

flag = True
while flag:
    print("enter 1 to add stock")
    print("enter 2 to remove stock")
    print("enter 3 to show stock’s contents")
    print("enter 4 to exit the program")
    user_input = input("")

    if user_input == "1":
        result = -1

        while result == -1:
            print_dict(my_dict)
            print("choose a number or product name to add to stock")
            product_input = input(" ").strip().lower()
            result = validate_add(product_input, my_dict)

        valid_input = -1

        while valid_input == -1:
            print("choose a number for this stock to increase it by")
            flag = 0

            try:
                num_stock = int(input(""))
                flag = 1
            except:
                print("Invalid")

            if flag == 1 and num_stock > 0:
                valid_input = 1

        if result == 1:
            number = int(product_input)
            key_value = dictionary_by_index(my_dict, number - 1)
            my_dict[key_value] += num_stock

        elif result == 2:
            key_value=product_input
            origin=dict[key_value]
            my_dict[product_input] += num_stock

        elif result == 3:
            key_value=product_input
            origin=dict[key_value]
            my_dict[product_input] = num_stock

        dict_to_file(my_dict, "stock.txt")
        print(f"Successfully added {num_stock} stocks to {key_value}!")

    elif user_input == "2":
        remove_element = -1

        while remove_element == -1 or remove_element == 3:
            print_dict(my_dict)
            print("choose a number or product name to remove from stock")
            product_input = input(" ").strip().lower()
            remove_element = validate_add(product_input, my_dict)

        if remove_element == 1:
            number = int(product_input)
            key_value = dictionary_by_index(my_dict, number - 1)
            original_stock_value = my_dict[key_value]

        elif remove_element == 2:
            key_value = product_input
            original_stock_value = my_dict[key_value]

        stock_removed = -1

        while stock_removed == -1:
            print("choose a number for this stock to decrease it by")
            flag = 0

            try:
                num_stock = int(input(""))
                flag = 1
            except:
                print("Invalid")

            if flag == 1 and num_stock > 0 and original_stock_value - num_stock >= 0:
                stock_removed = 1
            else:
                print("Invalid quantity")

        my_dict[key_value] -= num_stock
        dict_to_file(my_dict, "stock.txt")
        print(
            f"Successfully removed {num_stock} stocks from {key_value}, "
            f"now stock is {original_stock_value - num_stock}\n"
        )

    elif user_input == "3":
        print_dict(my_dict)
        print("Display shown successfully!\n")

    elif user_input == "4":
        print("Nice to have you as always, Goodbye!\n")
        flag = False

    else:
        print("Select suitable number\n")
        flag = True

    if user_input != "4":
        flag = True
