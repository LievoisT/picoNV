## Pico Setup Docs
* #### Install micropython
  * put the pico in bootsel mode and connect it to a pc
  * drag the micropython firmware onto the drive
  
* ### configure ide/repl
  * check which com port its connected to and edit the micropython plugin settings to match
  * can also use rshell to copy main.py over to the pico

* ### testing/misc
  * found the miniterm tool in pyserial really handy
  * ```shell
    python -m serial.tools.miniterm
    ```
  * activate the conda base env first probably
  * The file has to be named main.py for it to automatically run on startup
  * try not to accidentally send over a bunch of other project files that aren't necessary

