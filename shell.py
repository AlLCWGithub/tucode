import tucode

while True:
    text = input("tucode > ")
    response = tucode.run(text)
    print(response)