def are_you_sure(prompt, default="no"):
    if default.lower() == 'yes':
        suffix = "[YES|no]"
    else:
        suffix = "[yes|NO]"

    answer = input(
        "!!!!!!!!!!!!!!!!!!\n"
        "!!! BE CAREFUL !!!\n"
        "!!!!!!!!!!!!!!!!!!\n"
        "\n"
        f"{prompt}\n"
        "\n"
        f"Are you sure you want to proceed? {suffix} "
    ).strip().lower()

    if answer == '':
        answer = default

    while answer not in ['yes', 'no']:
        answer = input("Please type 'yes' or 'no' explicitly: ").strip().lower()

    return answer == 'yes'
