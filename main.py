import csv
import pickle
from src.Downloader import Downloader
from src.Dumper import Dumper


INPUT_FILE = 'in.csv'
THREAD_POOL_SIZE = 5


def main():
    input = read_input_file()

    driver = Dumper()
    driver.dumpCookies()

    cookies = pickle.load(open("cookies.pkl", "rb"))

    downloader = Downloader(input, cookies, THREAD_POOL_SIZE)
    downloader.startScaripng()


def read_input_file():
    with open(INPUT_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        return {key: int(value) for key, value in reader}


if __name__ == '__main__':
    main()


