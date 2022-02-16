from re import L
import sys

def interpret(script):
    global lastIf
    lines=splitWordLines(script)
    
    lastIf=None
    
    parse(lines)
    #print("\nFinished parsing")
    
    #print(lines)
    
    

def syntaxError(msg, lineNo):
    raise Exception(f"Syntax error in line: {lineNo}: {msg}")


def splitWordLines(script):
    scripLen=len(script)
    lines=[[""]]
    readingString=False
    readingExp=False
    readingBlock=False
    readingComment=False
    curlNest=0
    parenNest=0
    i=0
    
    for i in range(scripLen):
        char=script[i]
        
        if char == "\n":
            
            
            if readingComment:
                readingComment=False
                lines[-1]=[""]
                continue
            elif not (readingExp or readingBlock or readingString):
                continue
            
            
        
        elif char == '#' and lines[-1][0]=="":
            readingComment=True
            continue
        
        elif readingComment:
            continue
        
        elif readingBlock and not (readingExp or readingString):
            if char == "{":
                curlNest+=1

            elif char == "}":
                curlNest-=1
                if curlNest==0: #If final curly, add new line
                    readingBlock=False
                    lines[-1][-1]+=char
                    lines.append([""])
                    
                    continue
        
        elif readingExp and not (readingString or readingBlock):
            if char=="(":
                parenNest+=1
            elif char == ")":
                parenNest-=1
                if parenNest==0:
                    readingExp=False
                    lines[-1][-1]+=char
                    continue
        
        elif char==" " and not (readingExp or readingBlock or readingString):
            if len(lines[-1][0])==0: #If line starts with space, ignore first space
                continue
            elif i==scripLen-1: #If final char is space, break
                break
            elif script[i-1]==" ": #Ignore successive spaces
                i+1
                continue
            elif script[i+1]=="{":
                continue
            else:
                lines[-1].append("") # Add new word after single space
                continue
            
        elif char == ";" and not (readingBlock or readingString or readingExp): # Add a new line after ;
            lines.append([""])            
            continue
        
        elif char == "{" and not (readingExp or readingBlock or readingString):
            readingBlock=True
            curlNest=1
            lines.append([""])
        elif char == "}" and not (readingExp or readingString):
            if not readingBlock:
                syntaxError("Expected '{' before '}'")
            readingBlock=False

        elif char == '"':
            readingString = not readingString
        
        elif char == "(":
            readingExp=True
            parenNest=1
        elif char==")":
            if not readingExp:
                syntaxError("Expected '(' before ')'")
            
        lines[-1][-1]+=char
        
        
    
    if readingString:
        syntaxError("String never closed")
    
    elif readingExp:
        syntaxError("() Expression never closed")
    
    elif readingBlock:
        syntaxError("{} Expression never closed")
        
    
    lines.pop()

    return lines

def parse(lines):
    parsingIf=False
    parsingElse=False
    ifRes=None
    noLines=len(lines)
        
        
    for l in range(len(lines)):
        line=lines[l]
        
        if not line or not line[0]: #Remove empty lines
            lines.pop(l)
            l-=1
            continue
        
        elif line[0]=="ooaah":
            parsingIf=True
            ifRes=parseIf(line)
            continue
        
        elif ifRes and parsingIf:
            interpret(line[0][1:-1])
            parsingIf=False
            topLevel.lastIf=ifRes
            continue
        
        elif line[0]=="waa":
            if topLevel.lastIf is None:
                raise Exception(f"Excpected if statement before else")
            if parsingElse:
                raise Exception(f"Close else statement before another else")
            parsingElse=True
            continue
        
        elif not ifRes and parsingElse:
            interpret(line[0][1:-1])
            parsingElse=False
            continue
        
        
        for i in range(len(line)):
            word = line[i]
            
            if isinstance(word, int):
                continue
            
            if word == "":
                line.pop(i)
                i-=1
                continue
            
            if word=="hoo" and i==0:
                parseInput(line)
                i+=4
            elif word[:3]=="wee":
                wee(word) 
            elif word in topLevel.vars and i==0:
                if line[1]!="ooh":
                    raise Exception(f"Expected 'ooh' after variable redefinition")
                topLevel.vars[word]=monkEval(line[2:])
        
        
        
    #print(topLevel.vars)

def parseIf(line):
    if line[1][0]!='(' or line[1][-1]!=')':
        raise Exception("Exception in line {topLevel.lineNo}: Invalid if syntax")
    lastIf=monkEval(line[1][1:-1])
    topLevel.lastIf=lastIf
    return lastIf

def parseInput(line):
    if line[2]!="ooh":
        raise syntaxError(" Expected 'ooh' after variable definition")
    elif line[3][:7]=="eeeaah(":
        try:
            if topLevel.vars[line[3][7:-1]][0]!='"' and topLevel.vars[line[3][6:-1]][-1]!='"':
                raise syntaxError(": eeeaah takes type: string")
            else:
                prompt=topLevel.vars[line[3][7:-1]]
        except KeyError:
            prompt=line[3][7:-1]
            if prompt[0]!='"' and prompt[-1]!='"':
                syntaxError("eeeaah takes type: string")
        topLevel.vars[line[1]]=input(prompt[1:-1]+" ")
        
    else:
        topLevel.vars[line[1]]=monkEval(line[3:])

def wee(word):
    printedWord=word[4:-1]
    if printedWord[0]=='"' and printedWord[-1]=='"':
        print(printedWord[1:-1])
    else:
        try:
            printedWord=topLevel.vars[printedWord]
        except KeyError:
            if " " not in printedWord:            
                raise Exception(f"Error: Variable {printedWord} not defined")
            print(monkEval(printedWord))
            return
        if isinstance(printedWord, str):
            print(printedWord[1:-1])
        else:
            print(printedWord)

def monkEval(exp):
    if isinstance(exp, list):
        expWords=exp
    elif isinstance(exp, str):
        expWords=exp.split(" ")
    evalStr=""
    localVars={}
    
    for i in range(len(expWords)):
        word=expWords[i]
        
        try:
            localVars[word]=topLevel.vars[word]
            word=localVars[word]
            if isNumber(word):
                evalStr+=str(word)+" "
            elif isinstance(word, str):
                if (word[0]=='"' and word [-1]=='"') or (word[0]=="'" and word[-1]=="'"):
                    evalStr+=f"{word} "
                else:
                    evalStr+=f"'{word}' "
            else:
                evalStr+=localVars[word]+" "
        except KeyError:
            if word in logicalOperators:
                evalStr+= logicalOperators[word]+" "
            elif word in numericalOperators:
                evalStr += numericalOperators[word]+" "
            elif isNumber(word):
                evalStr+=str(word)+" "
            elif isinstance(word, str):
                if (word[0]=='"' and word [-1]=='"') or (word[0]=="'" and word[-1]=="'"):
                    evalStr+=f"{word} "
                else:
                    evalStr+=f"'{word}' "
            else:
                raise Exception(f"Exception in line {topLevel.lineNo}: Variable {word} not defined")
    return eval(evalStr)

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

logicalOperators={
        'oohooh' : '==',
        'woa' : 'not',
        'eee' : 'or',
        'oohwee' : 'and',
        'aah' : '>',
        'haa' : '<',
}

numericalOperators = {
    'eeeooh' : '+',
    'oohee' : '-',
    'haahee' : '/',
    'heehaa' : '*',
    'hoowaa' : '%',
}


with open(sys.argv[1]) as file:
#with open("givemeorange.monkeyc") as file: 
    script = file.read()

class Level:
    def __init__(self, lastIf=None, vars={}):
        self.lastIf=lastIf
        self.vars=vars
    

topLevel=Level()
interpret(script)

