import SansScript
while True:
    text = str(input('SansScript>> '))
    result, error = SansScript.Run(text,"test.sans")  
    if error:
        print(error.as_string())
    elif result:
        print(result)

    # main()