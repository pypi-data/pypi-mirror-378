import time

def HelloWorld(testo):
    string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\u0020"
    banana = ""

    for i in range(len(testo)):
        for j in range(len(string)):
            if testo[i] == string[j]:
                banana += string[j]
                print(banana)
                time.sleep(0.2)
                break
            else:
                print(banana + string[j])
                time.sleep(0.05)
