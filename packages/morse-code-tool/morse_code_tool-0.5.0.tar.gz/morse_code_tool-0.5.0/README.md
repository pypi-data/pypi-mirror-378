# Morse Code Generator  


## What it is  
This is a simple morse code generator.  
It takes text, converts it to morse code, saves it to a file, and plays back the generated audio  

## Usage  
Usage: `morse.py {-i | -o <filename> <text>}`  
```  
options:
  -h, --help            Show help message and exit
  -i, --interactive     Run in interactive mode to prompt for input.
  -o <filename> <text>, --output <filename> <text>
                        Provide a filename and text directly.
```  

## Dependencies  
- `sounddevice` = 0.5.2  
- `numpy` = 2.2.6  