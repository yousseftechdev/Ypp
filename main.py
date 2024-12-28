import ypp

def main() -> None:
    while True:
        cmd: str = input("yshell> ")
        result, error = ypp.run("stdio", cmd)
        
        if error: print(error.asString())
        else: print(result)

if __name__ == '__main__':
    main()