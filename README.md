# UgerScripts
A couple of scripts to replace the horrid default qstat / qconf functionalities


python qmon.py [-u <username>] [-w [-d <delay>]]
  - Running without arguments will produce a list of jobs running for whatever user runs the command.
  - Running with argument -u <username> will pass the parameter to qstat -u <username>, allows for -u "*" (quotes required)
  - Running with -w will run the scripts in a refreshing window, with a few checks to truncate lists if they will run off the page.  The default refresh delay is 3s, but that can be changed using -d <delay>
  - Produces an output in the following format:
================================= QUEUE HEALTH =================================
               Short: Load = 1.05, 496/701 nodes in use
                Long: Load = 1.25, 219/225 nodes in use
         Interactive: Load = 0.21, 36/44 nodes in use
================================= TASK ARRAYS ==================================
           Running: 9      Pending: 105    Errors: 0      ZOMBIES: 0
--------------------------------------------------------------------------------
   Job ID  Username  Project     Queue   RUN  PEND  FAIL    ZOMB  Time Elapsed
    66159  aganna    GCC         long      9   105     0     0      1:18:47:08
     85.8% [#####################=---]________________________________________

================================= INTERACTIVE ==================================
           Running: 1      Pending: 0      Errors: 0      ZOMBIES: 0
--------------------------------------------------------------------------------
   Job ID  Username  Project     Queue    Host           Status   Time Elapsed
    67958  aganna    QRLOGIN     inter    os-uger-2001   RUN          30:02:59

================================== OTHER JOBS ==================================
           Running: 0      Pending: 8      Errors: 0      ZOMBIES: 0
--------------------------------------------------------------------------------
   Job ID  Username  Project     Queue    Host           Status   Time Elapsed
    67643  aganna    SNPHHMEX    unkwn                   PEND         33:47:50
    67644  aganna    SNPHHMWG    unkwn                   PEND         33:47:50
...

python qhogs.py
  - Produces an output like the `bjobss` script we all loved so much:
       USERNAME   RUNNING  PENDING  ERRORS            CPU         MEM          IO
----------------------------------------------------------------------------------
         sripke   405      103      10          273:14:58     56471.7        44.6
        dbalick   30       14       0          1587:48:15   3100806.9         5.6
          jlane   29       70       0           402:18:43    937882.0      2313.6
        rsaxena   27       60       0           378:20:10   1388227.7      4122.5
       weisburd   24       39       0           230:16:41   9652741.6      5148.8
       aroselli   22       0        0           552:27:02   2834941.1      1186.6
...

----------------------------------------------------------------------------------
          TOTAL   669      466      151
