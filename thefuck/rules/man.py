def match(command):
    return command.script.strip().startswith('man ')


def get_new_command(command):
    if '3' in command.script:
        return command.script.replace("3", "2")
    if '2' in command.script:
        return command.script.replace("2", "3")

    split_cmd2 = command.script.split()
    split_cmd3 = split_cmd2[:]

    split_cmd2.insert(1, ' 2 ')
    split_cmd3.insert(1, ' 3 ')

    return ["".join(split_cmd3), "".join(split_cmd2)]
