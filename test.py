
line='%func%[(d123d+d456d)"123"%gho%[d4dd2dd4dd3d"123456,789001dd"]]'
stack=[]
buffer=''
for single in line:
    # str
    if single=='"':     
        if ('ps','"') in stack:
            start=stack.index(('ps','"'))
            editing=stack[start+1:]
            stack=stack[:start]
            
            stack.append(('string',''.join([i[1] for i in editing])))
        else:
            stack.append(('ps','"'))
    # list
    elif single=='[':
        stack.append(('ps','['))
    elif single==']':
        if ('ps','[') in stack:
            start=stack.index(('ps','['))
            if ('ps','"') in stack  and stack.index(('ps','"'))<start:continue
            editing=stack[start+1:]
            stack=stack[:start]
            stack.append(('list',[i for i in editing]))
        else:
            stack.append(('ps',']'))
    # eval
    elif single=='(':
        stack.append(('ps','('))
    elif single==')':
        if ('ps','(') in stack:
            start=stack.index(('ps','('))
            if ('ps','"') in stack  and stack.index(('ps','"'))<start:continue
            editing=stack[start+1:]
            stack=stack[:start]
            stack.append(('eval',[i[1] for i in editing]))
        else:
            stack.append(('ps',')'))
    elif single=='d':
        if ('ps','d') in stack:
            start=stack.index(('ps','d'))
            #print(('ps','"') in stack and stack.index(('ps','"'))<start)
            if ('ps','"') in stack and stack.index(('ps','"'))<start:continue
            editing=stack[start+1:]
            stack=stack[:start]
            stack.append(('int',int(''.join([i[1] for i in editing]))))
        else:
            stack.append(('ps','d'))
    # vars(inc func)
    elif single=='%':
        if ('ps','%') in stack:
            start=stack.index(('ps','%'))
            #print(('ps','"') in stack and stack.index(('ps','"'))<start)
            if ('ps','"') in stack and stack.index(('ps','"'))<start:continue
            editing=stack[start+1:]
            stack=stack[:start]
            stack.append(('vars',''.join([i[1] for i in editing])))
        else:
            stack.append(('ps','%'))
    else:
        stack.append(('sa',single))