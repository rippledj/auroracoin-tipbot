## +AURtip Auroracoin Forum Tipbot


This tipbot, written in python is for collecting post text from forums, finding +AURtip commands, and then processing transactions based on the details of the commands, similar to reddit-tipbot.


The database, api, and rpc interfaces are all abstracted so they can work with any forum that has an API (or forum that can be mechanized), mySQL and postgresql, and also any alt-coin rpc.


The main file is called tipbot.py.  This is where all objects are declared and the general flow of the package can be seen and managed.  The script functions by compiling a "payload" of commands found during it's parsing of the forum API in the payload.py.  The payload of commands is then processed in the payloadProcessor.py module, and messaging is handled using the messenger.py.  Finally, the banking processes are handled in the bank.py


##INSTALLATION


1) install the database schema included in the database directory.

2) Simply copy the source code to a directory in your server.

3) Edit the api_abstraction_default.py, sql_abstraction_default.py, and rpc_abstraction_default.py files to match your desired settings.

4) run the script using "python tipbot.py"


 
