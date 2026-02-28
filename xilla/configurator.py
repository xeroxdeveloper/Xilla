import os
import re
import string
import sys
import typing

def tty_print(text: str, tty: bool):
    print(text if tty else re.sub('\\033\\[[0-9;]*m', '', text))

def tty_input(text: str, tty: bool) -> str:
    return input(text if tty else re.sub('\\033\\[[0-9;]*m', '', text))

def api_config(tty: typing.Optional[bool]=None):
    from . import main
    from ._internal import print_banner
    if tty is None:
        print('\x1b[0;91mThe quick brown fox jumps over the lazy dog\x1b[0m')
        tty = False
    if tty:
        print_banner('banner.txt')
    tty_print('\x1b[0;95mWelcome to Xilla Userbot!\x1b[0m', tty)
    tty_print('\x1b[0;96m1. Go to https://my.telegram.org and login\x1b[0m', tty)
    tty_print('\x1b[0;96m2. Click on \x1b[1;96mAPI development tools\x1b[0m', tty)
    tty_print('\x1b[0;96m3. Create a new application, by entering the required details\x1b[0m', tty)
    tty_print('\x1b[0;96m4. Copy your \x1b[1;96mAPI ID\x1b[0;96m and \x1b[1;96mAPI hash\x1b[0m', tty)
    while (api_id := tty_input('\x1b[0;95mEnter API ID: \x1b[0m', tty)):
        if api_id.isdigit():
            break
        tty_print('\x1b[0;91mInvalid ID\x1b[0m', tty)
    if not api_id:
        tty_print('\x1b[0;91mCancelled\x1b[0m', tty)
        sys.exit(0)
    while (api_hash := tty_input('\x1b[0;95mEnter API hash: \x1b[0m', tty)):
        if len(api_hash) == 32 and all((symbol in string.hexdigits for symbol in api_hash)):
            break
        tty_print('\x1b[0;91mInvalid hash\x1b[0m', tty)
    if not api_hash:
        tty_print('\x1b[0;91mCancelled\x1b[0m', tty)
        sys.exit(0)
    main.save_config_key('api_id', int(api_id))
    main.save_config_key('api_hash', api_hash)
    tty_print('\x1b[0;92mAPI config saved\x1b[0m', tty)