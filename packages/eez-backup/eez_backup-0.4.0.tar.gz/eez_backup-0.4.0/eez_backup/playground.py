from pathlib import Path




def main():
    for ps in Path("~/Datasets").expanduser().glob("*.json"):
        print(ps)

if __name__ == "__main__":
    main()