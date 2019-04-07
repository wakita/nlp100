def chapter(t):
    print(f'Chapter {t}')

def title(t):
    print(f'\n# Problem - {t}\n')

import subprocess

def system(command, **options):
    proc = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            **options)
    return proc.communicate()[0].decode('utf-8')

def cat(filepath):
    return system(f'cat {filepath}')
