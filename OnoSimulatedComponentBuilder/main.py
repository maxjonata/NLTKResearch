def get_verbs_list_from_mobypos():
    with open("mobypos.txt", 'r', encoding="utf-8") as file:
        lines = file.readlines()

    verbs = set()
    for line in lines:
        parts = line.strip('\n').split('\\')
        if len(parts) > 1 and parts[1] == "V" or parts[1] == "t" or parts[1] == "i": # V stands for participle verbs, t stands for transitive verbs, i stands for intransitive verbs on mobypos
            verbs.add(parts[0])

    return verbs

def write_file_list(word_list, name):
    with open(name, 'w', encoding="utf-8") as file:
        for x, item in enumerate(word_list):
            file.write(item)
            if x != len(word_list)-1:
                file.write('\n')

def get_nouns_list_from_mobypos():
    with open("mobypos.txt", 'r', encoding="utf-8") as file:
        lines = file.readlines()

    nouns = set()
    for line in lines:
        parts = line.strip('\n').split('\\')
        if len(parts) > 1 and parts[1] == "N": # N stands for noun on mobypos
            nouns.add(parts[0])

    return nouns

def main():
    verbs = get_verbs_list_from_mobypos()
    write_file_list(verbs, "verbs.txt")

if __name__ == "__main__":
    main()