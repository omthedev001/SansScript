import SansScript
while True:
    text = input('SansScript> ')
    result, error = SansScript.run(text,"test.sans")  
    if error:
        print(error.as_string())
    else:
        print(result)
