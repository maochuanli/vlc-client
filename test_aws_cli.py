import sys
import os

if os.environ.get('LC_CTYPE', '') == 'UTF-8':
    os.environ['LC_CTYPE'] = 'en_US.UTF-8'
import awscli.clidriver
import s3transfer

def main():
    return awscli.clidriver.main()


if __name__ == '__main__':
    sys.exit(main())