import test as SansScript

while True:
    text = str(input("SansScript>> "))
    if text.strip() == "" : continue
    result, error = SansScript.run("test.sans",text)
    
    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(f'SANSCRIPT RESULT >> {result.elements[0]} <<')
        else:
            print(f'SANSCRIPT RESULT >> {result} <<')

    # main()
