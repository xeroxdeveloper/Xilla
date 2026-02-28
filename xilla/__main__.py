import getpass
import os
import subprocess
import sys
from ._internal import restart
if getpass.getuser() == 'root' and '--root' not in ' '.join(sys.argv) and all((trigger not in os.environ for trigger in {'DOCKER', 'GOORM'})):
    print('\033[38;2;255;50;50m🚫' * 15)
    print('Внимание! Вы пытаетесь запустить Xilla от имени root. Это небезопасно.')
    print('Please, create a new user and restart script')
    print('If this action was intentional, pass --root argument instead')
    print('\033[38;2;255;50;50m🚫' * 15)
    print()
    print('Type force_insecure to ignore this warning')
    if input('> ').lower() != 'force_insecure':
        pass

def deps():
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '-q', '--disable-pip-version-check', '--no-warn-script-location', '-r', 'requirements.txt'], check=True)
if sys.version_info < (3, 8, 0):
    print('🚫 Error: you must use at least Python version 3.8.0')
elif __package__ != 'xilla':
    print('🚫 Error: you cannot run this as a script; you must execute as a package')
else:
    try:
        import hikkatl
    except Exception:
        pass
    else:
        try:
            import hikkatl
            if tuple(map(int, hikkatl.__version__.split('.'))) < (2, 0, 4):
                raise ImportError
            import hikkapyro
            if tuple(map(int, hikkapyro.__version__.split('.'))) < (2, 0, 103):
                raise ImportError
        except ImportError:
            print('\033[38;2;0;210;255m[Xilla Alpaca] \033[38;2;34;157;229m⚙️ Установка библиотек...\033[0m')
            deps()
            restart()
    try:
        from . import log
        log.init()
        from . import main
    except ImportError as e:
        print(f'{str(e)}\n🔄 Attempting dependencies installation... Just wait ⏱')
        deps()
        restart()
    if 'XILLA_DO_NOT_RESTART' in os.environ:
        del os.environ['XILLA_DO_NOT_RESTART']
    main.xilla.main()