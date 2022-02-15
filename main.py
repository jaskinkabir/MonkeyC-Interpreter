import sys

def interpret(script):
    global lastIf
    lines=splitWordLines(script)
    
    lastIf=None
    
    parse(lines)
    #print("\nFinished parsing")
    
    #print(lines)
    
    



def splitWordLines(script):
    lines=[[""]]    
    readingString=False
    readingExp=False
    readingBlock=False
    curlNest=0
    expNest=0
    i=0
    while(i<len(script)):
        lineNo=len(lines)
        char=script[i]
        if char == "\n" or char == "":
            i+=1
            continue
        
        elif char==" " and not readingString and not readingExp and not readingBlock:
            if i==0 or i==len(script)-1:
                i+=1
                continue
            elif script[i+1]==" " or script[i-1]==" ": #Ignore successive spaces
                i+=1
                continue
            lines[-1].append("") # Add a new word after a single space
            i+=1
            continue        
        
        elif char == ";" and not readingBlock: # Add a new line after ;
            lines.append([""])
            i+=1
            continue
        
        elif char == "{":
            if curlNest==0:
                lines.append([""])
            lines[-1][-1]+=char
            curlNest+=1
            i+=1
            char=""
            for i in range(i,len(script)):
                charb = script[i]
                
                if charb == "{":
                    curlNest+=1
                    lines[-1][-1]+=charb
                
                elif charb == "}":
                    curlNest-=1
                    lines[-1][-1]+=charb
                    if curlNest==0:
                        lines.append([""])
                        charb=""
                        break
                else:
                    lines[-1][-1]+=charb
            
        elif char == '"': # Start reading string after "
            readingString=not readingString
        elif char == "(":
            readingExp=True
        elif char == ")":
            if not readingExp:
                raise Exception(f"Exception in line {lineNo}: Expected '(' before ')'")
            readingExp=False
        
        if char!="":
            lines[-1][-1]+=char
        i+=1    
    
    if readingString:
        raise Exception("String never closed")
    
    if readingExp:
        raise Exception("() Expression never closed")
    
    for line in lines:
        if not line or not line[0]:
            lines.remove(line)
        for word in line:
            if not word:
                line.remove(word)

    return lines

def parse(lines):
    global lineNo
    lineNo=1
    parsingCodeBlock=False
    parsingIf=False
    parsingElse=False
    ifRes=None
    global lastIf
    for l in range(len(lines)):
        line=lines[l]
        if not line or not line[0]: #Remove empty lines
            lines.pop(l)
            l-=1
            continue
        
        elif line[0][0]=="#": #Ignore comments
            continue
        
        elif line[0]=="ooaah":
            parsingCodeBlock=True
            parsingIf=True
            
            if line[1][0]!='(' or line[1][-1]!=')':
                raise Exception("Exception in line {lineNo}: Invalid if syntax")
            ifRes = monkEval(line[1][1:-1])
            topLevel.lastIf=ifRes
            continue
        
        elif ifRes and parsingIf:
            interpret(line[0][1:-1])
            parsingIf=False
            parsingCodeBlock=False
            topLevel.lastIf=ifRes
            continue
        
        elif line[0]=="waa":
            if topLevel.lastIf is None:
                raise Exception("Exception in line {lineNo}: Excpected if statement before else")
            if parsingElse:
                raise Exception("Exception in line {lineNo}: Close else statement before another else")
            parsingCodeBlock=True
            parsingElse=True
            continue
        
        elif not ifRes and parsingElse:
            interpret(line[0][1:-1])
            parsingElse=False
            parsingCodeBlock=False
            continue
        
        
        parsingDefinition=False
        for i in range(len(line)):
            word = line[i]
            
            
            if word == "":
                line.pop(i)
                i-=1
                continue
            
            if word=="hoo" and i==0:
                parsingDefinition=True
                if line[2]!="ooh":
                    raise Exception("Exception in line {lineNo}: Expected 'ooh' after variable definition")
                elif line[3][:7]=="eeeaah(":
                    try:
                        if topLevel.globalVars[line[3][7:-1]][0]!='"' and topLevel.globalVars[line[i+3][6:-1]][-1]!='"':
                            raise Exception(f"Exception in line {lineNo}: eeeaah takes type: string")
                        else:
                            prompt=topLevel.globalVars[line[i+3][7:-1]]
                    except KeyError:
                        prompt=line[3][7:-1]
                        if prompt[0]!='"' and prompt[-1]!='"':
                            raise Exception(f"Exception in line {lineNo}: eeeaah takes type: string")
                    topLevel.globalVars[line[i+1]]=input(prompt[1:-1]+" ")
                    
                else:
                    topLevel.globalVars[line[1]]=line[3]
                i+=4
            elif word[:3]=="wee":
                wee(word) 
                pass
            elif word in topLevel.globalVars and i==0:
                if line[1]!="ooh":
                    raise Exception(f"Exception in line {lineNo}: Expected 'ooh' after variable definition")
                topLevel.globalVars[word]=monkEval(line[2:])
        
        
        lineNo+=1        
    #print(topLevel.globalVars)
    
def wee(word):
    printedWord=word[4:-1]
    if printedWord[0]=='"' and printedWord[-1]=='"':
        print(printedWord[1:-1])
    else:
        try:
            printedWord=topLevel.globalVars[printedWord]
        except KeyError:
            if " " not in printedWord:            
                raise Exception(f"Exception in line {lineNo}: Variable {printedWord} not defined")
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
                evalStr+=f"'{word}' "
            else:
                evalStr+=localVars[word]+" "
        except KeyError:
            if word in logicalOperators:
                evalStr+= logicalOperators[word]+" "
            elif word in numericalOperators:
                evalStr += numericalOperators[word]+" "
            elif isNumber(word):
                evalStr+=word+" "
            elif word[0]=='"' and word[-1]=='"':
                evalStr+=word+" "
            else:
                raise Exception(f"Exception in line {lineNo}: Variable {word} not defined")
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
        self.lastIf=None
        self.globalVars={}
    

topLevel=TopLevel()
interpret(script)

