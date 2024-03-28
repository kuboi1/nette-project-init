import subprocess as sp


if __name__ == '__main__':
    print('Verifying packages...')
    print()
    sp.run(['pip', 'install', '--no-cache-dir', '-r', 'packages.txt'], shell=True)
    print()
    print('Packages verified.')