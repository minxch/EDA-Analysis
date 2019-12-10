Instructions for using the Data Interpreter:

[Beginning]

    WARN:
    WARN: In order to run the program, you must have Python installed!
    WARN:

    [run.bat]
        If you are opening from the command prompt, skip to [Command Line]
        
        The run.bat is a simple script file that will automatically open the program for you in a new
        Command Prompt window, so that you don't have to navigate to your testing folder manually.

	Keep run.bat in the same location as your program!

        It runs the python command to open the program, then pauses at the end of usage so that you can
        evaluate the window log.

    [Command Line]
        If you are running from the Command Prompt manually.

        Open Command Prompt, and type:
            "
                cd [Folder Location]
            "
        [Folder Location] is where your Data Interpreter program is located.

        In my case, since I used OneDrive, my command was: 
            "
                cd "C:\Users\snowm\OneDrive\Normalized Data Interpreter 2.2"
            "

        Once in the correct location, simply run the python file by issuing the command:
            "
                python [programfilename]
            "
        [programfilename] is what your Data Interpreter program is named (including file extension)

        In my case, I named my program "main.py", so:
            "
                python main.py
            "
    
[Running the Program]

    Preface: If you have a bad input type such as:
        You added strings or letters to your integer input
        You pressed Enter before typing anything
    , your program will stop, and you will have to start over.
    In some cases, where you input an answer of the correct type, but out of scope, it will just re-prompt you.

    You will be prompted by a message asking for a path to a folder of files.
    By giving the location, the program will automatically process the folder given, then the files
    in that given folder.

    When selecting a folder, please make sure that EVERY file involved is in the proper format.
    This means that you cannot have other folders or random files in the path given to the program,
    otherwise the program will not be able to process the files and stop.

    This program assumes that you are inputting the correct path.

    Acceptable examples of paths include:
        Folder name in the same location: 
            testNormalizer
        Path to the folder name: 
            C:\Users\snowm\OneDrive\Normalized Data Interpreter 2.2\testNormalizer
        Path from a folder in the same location: 
            exampleFolder\testNormalizer

    Once the folder is accepted, the window will print the files that were processed, so that you can
    double-check that you've inputted the correct files.

    The next prompt will ask if you would like to normalize your data.

    If you do not normalize your data, then the program will process the data using the files given, unaltered.

    Type the answer you'd like, then press Enter.
    If you will not normalize, skip to [After Normalizing]

    [Normalizing]
        You are here because you answered with "1" for "Yes" to normalizing your files.
        You will now be asked for what type of normalization you prefer.
        Min-Max normalization and Z-Score normalization is available.
        Type the answer you'd like, then press Enter.

    [After Normalizing]
        You are now prompted for what type of calculation features that you want to perform on
        your data.
        Each option indicates a different combination of calculations that you may perform.
        Type the answer you'd like, then press Enter.

    [After Calculations]
        You will be prompted if you are processing data in pairs or individually.
        Pairs are detected by seeing the "Session" tag in each data file name, and matching them by number.
        Type the answer you'd like, then press Enter.
    
    [Parameters]
        You will now be prompted in a series of questions asking for the parameters of the window you'd like to calculate.
        Each line of data counts for 0.25 seconds, since the data was taken every fourth of a second.

        "Enter the timeframe you wish to section the data with: (how much data per section)"
            This asks for how many lines of data you'd like to collectively perform calculations on every iteration of windows.

        "Enter the increment you wish to section the data with: (how much data in between sections)"
            This asks for how many lines of data you'd like the window to move forward to perform calculations on the next set.

        "Enter how many windows you wish to section the data with: (0 for no limit)"
            This asks for how many windows you want to perform calculations on.
            If you enter 0, then it will keep making windows until the file ends in each file, making sure to keep each window at
            full size.

        "Enter the position you wish to begin sectioning: (0 for the beginning)"
            This asks for where you want to start the windows from.
            If you enter 0, then it will start from the beginning of the data file.
            If you enter a value greater than 0, 100, for example, it will start from the 100th data line, or 25 seconds.

    [Directional Agreement and Signal Matching]
        If you are not calculating in pairs, skip this section.

        You will be prompted if you'd like to perform calculations for Directional Agreement and Signal Matching.

        Directional Agreement finds intervals in which the data pairs align or unalign with each other, then also lists
        the amount of time in that interval.

        Signal Matching finds the difference between the two data pairs on every line, and tells you the overall average
        difference in the data.

[Outputs]
    The rest of the program now runs on its own, then finalizes by writing the new output files to a new folder in the root location
    named "outputs".
    In "outputs", there will be a folder named as the date that the program ran, for example "1970-1-1"
    Then in that folder, there will be another folder named as the time that the program ran, for example "1h_30m_45s"
    
    The outputs are organized this way so that you can do multiple runs in any time period without having to worry about
    overwrites or mixed data outputs.

    As an example, the final path will be "\outputs\1970-1-1\1h_30m_45s\".



Thank you for using the Data Interpreter! :)