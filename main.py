from re import L
import sys

def interpret(script, startingLine=1):
    global lastIf
    lines=splitWordLines(script)
    
    lastIf=None
    
    parse(lines, startingLine)
    #print("\nFinished parsing")
    
    #print(lines)
    
    

def syntaxError(msg, lineNo):
    raise Exception(f"Syntax error in line: {lineNo}: {msg}")


def splitWordLines(script, startingLine=1):
    scripLen=len(script)
    lines=[[""]]
    lineNo=startingLine    
    readingString=False
    readingExp=False
    readingBlock=False
    readingComment=False
    curlNest=0
    parenNest=0
    i=0
    startingCurls=[]
    startingExps=[]
    
    for i in range(scripLen):
        char=script[i]
        
        if char == "\n":
            lineNo+=1
            
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
                startingCurls.append(lineNo) 
            elif char == "}":
                curlNest-=1
                startingCurls.pop()
                if curlNest==0: #If final curly, add new line
                    readingBlock=False
                    lines[-1][-1]+=char
                    lines[-1].append(lineNo)
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
            lines[-1].append(lineNo)
            lines.append([""])            
            continue
        
        elif char == "{" and not (readingExp or readingBlock or readingString):
            startingCurls.append(lineNo)
            readingBlock=True
            curlNest=1
            lines[-1].append(lineNo)
            lines.append([""])
        elif char == "}" and not (readingExp or readingString):
            if not readingBlock:
                syntaxError("Expected '{' before '}'", lineNo)
            readingBlock=False
            startingCurls.pop()

        elif char == '"':
            startingString=lineNo
            readingString = not readingString
            startingString=lineNo
        
        elif char == "(":
            readingExp=True
            parenNest=1
            startingExp=lineNo
        elif char==")":
            if not readingExp:
                syntaxError("Expected '(' before ')'", lineNo)
            
        lines[-1][-1]+=char
        
        
    
    if readingString:
        syntaxError("String never closed", startingString)
    
    elif readingExp:
        syntaxError("() Expression never closed", startingExp)
    
    elif readingBlock:
        if len(startingCurls)==1:
            syntaxError("{} Expression never closed", startingCurls[0])
        elif len(startingCurls)==2:
            syntaxError("{} Expression never closed", startingCurls[1])
        else:
            syntaxError("{} Expression never closed", startingCurls[-(curlNest+1)])
        
    
    lines.pop()

    return lines

def parse(lines, startingLine=1):
    parsingIf=False
    parsingElse=False
    ifRes=None
    lineNo=startingLine
    noLines=len(lines)
        
        
    for l in range(len(lines)):
        line=lines[l]
        
        if line[0]=="{":
            lineNo
        lineNo=line[-1]+startingLine-1
        
        if not line or not line[0]: #Remove empty lines
            lines.pop(l)
            l-=1
            continue
        
        elif line[0]=="ooaah":
            parsingIf=True
            ifRes=parseIf(line)
            continue
        
        elif ifRes and parsingIf:
            interpret(line[0][1:-1], startingLine=lineNo)
            parsingIf=False
            topLevel.lastIf=ifRes
            continue
        
        elif line[0]=="waa":
            if topLevel.lastIf is None:
                raise Exception(f"Exception in line {lineNo}: Excpected if statement before else")
            if parsingElse:
                raise Exception(f"Exception in line {lineNo}: Close else statement before another else")
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
                parseInput(line, lineNo)
                i+=4
            elif word[:3]=="wee":
                wee(word) 
            elif word in topLevel.globalVars and i==0:
                if line[1]!="ooh":
                    raise Exception(f"Exception in line {lineNo}: Expected 'ooh' after variable redefinition")
                topLevel.globalVars[word]=monkEval(line[2:])
        
        
        lineNo+=1
    #print(topLevel.globalVars)

def parseIf(line):
    if line[1][0]!='(' or line[1][-1]!=')':
        raise Exception("Exception in line {topLevel.lineNo}: Invalid if syntax")
    lastIf=monkEval(line[1][1:-1])
    topLevel.lastIf=lastIf
    return lastIf

def parseInput(line, lineNo):
    if line[2]!="ooh":
        raise syntaxError(" Expected 'ooh' after variable definition", lineNo)
    elif line[3][:7]=="eeeaah(":
        try:
            if topLevel.globalVars[line[3][7:-1]][0]!='"' and topLevel.globalVars[line[3][6:-1]][-1]!='"':
                raise syntaxError(": eeeaah takes type: string", lineNo)
            else:
                prompt=topLevel.globalVars[line[3][7:-1]]
        except KeyError:
            prompt=line[3][7:-1]
            if prompt[0]!='"' and prompt[-1]!='"':
                syntaxError("eeeaah takes type: string", lineNo)
        topLevel.globalVars[line[1]]=input(prompt[1:-1]+" ")
        
    else:
        topLevel.globalVars[line[1]]=monkEval(line[3:])

def wee(word):
    printedWord=word[4:-1]
    if printedWord[0]=='"' and printedWord[-1]=='"':
        print(printedWord[1:-1])
    else:
        try:
            printedWord=topLevel.globalVars[printedWord]
        except KeyError:
            if " " not in printedWord:            
                raise Exception(f"Exception in line {topLevel.lineNo}: Variable {printedWord} not defined")
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
    
    #print(exp)
    
    for i in range(len(expWords)):
        word=expWords[i]
        #print(word)
        
        try:
            localVars[word]=topLevel.globalVars[word]
            word=localVars[word]
            if isNumber(word):
                evalStr+=localVars[word]+" "
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
    #print(f"evalStr: {evalStr}")
    #print (eval(evalStr))
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

class TopLevel:
    def __init__(self):
        self.lineNo=1
        self.lastIf=None
        self.globalVars={}
    

topLevel=TopLevel()
interpret(script)

