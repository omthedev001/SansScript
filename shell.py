import SansScript

while True:
    try:
        text = str(input("SansScript>> "))
        if text.strip() == "" : continue
        result, error = SansScript.Run(text, "test.sans")

        if error:
            print(error.as_string())
        elif result:
            if len(result.elements) == 1:
                print(repr(result.elements[0]))
            else:
                print(repr(result))
    except KeyboardInterrupt:
        print("\nExiting SansScript Shell...")
        break
    # main()
