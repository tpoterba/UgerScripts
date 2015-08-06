# UgerScripts
A couple of scripts to replace the horrid default qstat / qconf functionalities


python qmon.py [-u 'username'] [-w [-d 'delay']]
  - Running without arguments will produce a list of jobs running for whatever user runs the command.
  - Running with argument -u <username> will pass the parameter to qstat -u <username>, allows for -u "*" (quotes required)
  - Running with -w will run the scripts in a refreshing window, with a few checks to truncate lists if they will run off the page.  The default refresh delay is 3s, but that can be changed using -d <delay>


python qhogs.py
  - Produces an output like the `bjobss` script we all loved so much
