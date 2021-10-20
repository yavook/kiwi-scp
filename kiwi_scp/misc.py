from typing import Any, Type

import click


def user_query(description: str, default: Any, cast_to: Type[Any] = str):
    # prompt user as per argument
    while True:
        try:
            str_value = input(f"Enter {description} [{default}] ").strip()
            if str_value:
                return cast_to(str_value)
            else:
                return default

        except EOFError:
            click.echo("Input aborted.")
            return default

        except Exception as e:
            click.echo(f"Invalid input: {e}")


def _surround(string, bang):
    midlane = f"{bang * 3} {string} {bang * 3}"
    sidelane = bang * len(midlane)

    return f"{sidelane}\n{midlane}\n{sidelane}"


def _emphasize(lines):
    if isinstance(lines, list):
        return '\n'.join([_emphasize(line) for line in lines])
    elif lines:
        return f">>> {lines} <<<"
    else:
        return lines


def are_you_sure(prompt, default="no"):
    if default.lower() == 'yes':
        suffix = "[YES|no]"
    else:
        suffix = "[yes|NO]"

    answer = input(
        f"{_surround('MUST HAVE CAREFULING IN PROCESS', '!')}\n"
        f"\n"
        f"{_emphasize(prompt)}\n"
        f"\n"
        f"Are you sure you want to proceed? {suffix} "
    ).strip().lower()

    if answer == '':
        answer = default

    while answer not in ['yes', 'no']:
        answer = input("Please type 'yes' or 'no' explicitly: ").strip().lower()

    return answer == 'yes'
