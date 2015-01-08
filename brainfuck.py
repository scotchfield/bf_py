# threaded brainfuck with assertions
# *: initialize a pc here operating in the same memory space
#    moving outside the program or into another thread's space will terminate
#      the specific process
# !: assert if the current memory at the pointer is non-zero

import random

class Brainfuck:
    MEM_SIZE = 20
    verbose = False
    accepting = [ '>', '<', '+', '-', '.', ',', '[', ']', '*', '!' ]

    def __init__( self ):
        self.pointer = []
        self.pc = []
        self.input_stack = []
        self.loop_ref = {}
        self.memory_bounds = []
        self.memory = [ 0 ] * Brainfuck.MEM_SIZE
        self.program = ''

    def _StoreLoopAddress( self ):
        self.loop_ref = {}
        open_loop_stack = []
        for x in range( len( self.program ) ):
            if self.program[ x ] == '[':
                open_loop_stack.append( x )
            elif self.program[ x ] == ']':
                open_loop = open_loop_stack.pop()
                self.loop_ref[ open_loop ] = x
                self.loop_ref[ x ] = open_loop

    def _InitializeThreads( self ):
        self.memory_bounds = []
        self.pointer = []
        self.pc = []
        last_pc = -1
        for x in range( len( self.program ) ):
            if self.program[ x ] == '*' or x == 0:
                if last_pc > -1:
                    self.memory_bounds.append( ( last_pc, x ) )
                self.pointer.append( 0 )
                self.pc.append( x )
                last_pc = x
        self.memory_bounds.append( ( last_pc, x ) )

    def SetProgram( self, program ):
        self.program = program
        self._StoreLoopAddress()
        self._InitializeThreads()

    def SetInputStack( self, input_stack ):
        self.input_stack = input_stack

    def Alive( self ):
        if len( self.pointer ):
            return True
        return False

    def Run( self ):
        while self.Alive():
            self.Step()

    def Step( self ):
        if not self.Alive():
            return False

        path = random.randint( 0, len( self.pc ) - 1 )
        ( mem_min, mem_max ) = self.memory_bounds[ path ]
        if self.pc[ path ] < mem_min or self.pc[ path ] >= mem_max:
            del self.pointer[ path ]
            del self.pc[ path ]
            del self.memory_bounds[ path ]
            return True

        cmd = self.program[ self.pc[ path ] ]
        if self.verbose:
            if cmd in Brainfuck.accepting:
                print 'T{0}: {1} {2} '.format(
                    str( path ), cmd, str( self.pc[ path ] ) ),

        if cmd == '>':
            self.pointer[ path ] = ( self.pointer[ path ] + 1 ) % \
                Brainfuck.MEM_SIZE
        elif cmd == '<':
            self.pointer[ path ] = ( self.pointer[ path ] - 1 ) % \
                Brainfuck.MEM_SIZE
        elif cmd == '+':
            self.memory[ self.pointer[ path ] ] = \
                ( self.memory[ self.pointer[ path ] ] + 1 ) % 256
        elif cmd == '-':
            self.memory[ self.pointer[ path ] ] = \
                ( self.memory[ self.pointer[ path ] ] - 1 ) % 256
        elif cmd == '.':
            print chr( self.memory[ self.pointer[ path ] ] ),
        elif cmd == ',':
            self.memory[ self.pointer[ path ] ] = self.input_stack.pop()
        elif cmd == '[':
            if self.memory[ self.pointer[ path ] ] == 0:
                self.pc[ path ] = self.loop_ref[ self.pc[ path ] ]
        elif cmd == ']':
            if self.memory[ self.pointer[ path ] ] != 0:
                self.pc[ path ] = self.loop_ref[ self.pc[ path ] ] - 1
        elif cmd == '!':
            if self.memory[ self.pointer[ path ] ] != 0:
                raise Exception, "Fuck!"

        self.pc[ path ] += 1
        if self.verbose:
            if cmd in Brainfuck.accepting:
                print self.memory,
                print '  %d' % ( self.pointer[ path ] )





bf_prog = "*>+++++++++[<++++++++>-]<.>+++++++[<++++>-]<+.+++++++..+++.[-]>++++++++[<++++>-]<.#>+++++++++++[<+++++>-]<.>++++++++[<+++>-]<.+++.------.--------.[-]>++++++++[<++++>-]<+.[-]++++++++++."

bf_deadlock = """
The first position in memory is always set to nonzero to allow the threads to run forever
Second position in memory is flag1
Third position in memory is flag2
Fourth position in memory is c which is the critical region

*+[>          First thread is T1
+             loc0: flag1 := true
>             goto loc2
-[+-]+        when flag2 == false goto loc3
>!+-          Verify that c is zero and increment/decrement
<<-           flag1 := false
<]            Back to the start and check the first bit

*+[>>         Second thread is T2
+             loc0: flag2 := true
<             goto loc2
-[+-]+        when flag1 == false goto loc3
>>!+-         Verify that c is zero and increment/decrement
<-            flag2 := false
<<]           Back to the start and check the first bit
"""

bf_666 = '*>+++++++++[<++++++>-]<...>++++++++++*.>>>>>>>>+++++++++[<++++++>-]<...>++++++++++'

bf_locking = """

*+>>>+<<<[
  >>>>>        Go to the WHO memory location
  >[-]+>[-]<<  Set memory after WHO to 1 0 for conditional and return to WHO
  [  <<-<<-     If WHO is 1 then unlock and let T2 loose
    >>>>>-]>
  [< <<-<-      If WHO is 0 then unlock and let T3 loose
    >>>>->]<<
  <
  -[+-]
  <<<<
]
*+>+<   [>[]+>>!+>+<<<<]
*+>>+<< [>>[]+>!+>+<<<<]
*>>>>>+[-+]
*>>>>>>>>>>+[-+]
*>>>>>>>>>>+[-+]
*>>>>>>>>>>+[-+]
"""

bf_99beer = """
*>+++++++++[<+++++++++++>-]<[>[-]>[-]<<[>+>+<<-]>>[<<+>>-]>>>
[-]<<<+++++++++<[>>>+<<[>+>[-]<<-]>[<+>-]>[<<++++++++++>>>+<
-]<<-<-]+++++++++>[<->-]>>+>[<[-]<<+>>>-]>[-]+<<[>+>-<<-]<<<
[>>+>+<<<-]>>>[<<<+>>>-]>[<+>-]<<-[>[-]<[-]]>>+<[>[-]<-]<+++
+++++[<++++++<++++++>>-]>>>[>+>+<<-]>>[<<+>>-]<[<<<<<.>>>>>-
]<<<<<<.>>[-]>[-]++++[<++++++++>-]<.>++++[<++++++++>-]<++.>+
++++[<+++++++++>-]<.><+++++..--------.-------.>>[>>+>+<<<-]>
>>[<<<+>>>-]<[<<<<++++++++++++++.>>>>-]<<<<[-]>++++[<+++++++
+>-]<.>+++++++++[<+++++++++>-]<--.---------.>+++++++[<------
---->-]<.>++++++[<+++++++++++>-]<.+++..+++++++++++++.>++++++
++[<---------->-]<--.>+++++++++[<+++++++++>-]<--.-.>++++++++
[<---------->-]<++.>++++++++[<++++++++++>-]<++++.-----------
-.---.>+++++++[<---------->-]<+.>++++++++[<+++++++++++>-]<-.
>++[<----------->-]<.+++++++++++..>+++++++++[<---------->-]<
-----.---.>>>[>+>+<<-]>>[<<+>>-]<[<<<<<.>>>>>-]<<<<<<.>>>+++
+[<++++++>-]<--.>++++[<++++++++>-]<++.>+++++[<+++++++++>-]<.
><+++++..--------.-------.>>[>>+>+<<<-]>>>[<<<+>>>-]<[<<<<++
++++++++++++.>>>>-]<<<<[-]>++++[<++++++++>-]<.>+++++++++[<++
+++++++>-]<--.---------.>+++++++[<---------->-]<.>++++++[<++
+++++++++>-]<.+++..+++++++++++++.>++++++++++[<---------->-]<
-.---.>+++++++[<++++++++++>-]<++++.+++++++++++++.++++++++++.
------.>+++++++[<---------->-]<+.>++++++++[<++++++++++>-]<-.
-.---------.>+++++++[<---------->-]<+.>+++++++[<++++++++++>-
]<--.+++++++++++.++++++++.---------.>++++++++[<---------->-]
<++.>+++++[<+++++++++++++>-]<.+++++++++++++.----------.>++++
+++[<---------->-]<++.>++++++++[<++++++++++>-]<.>+++[<----->
-]<.>+++[<++++++>-]<..>+++++++++[<--------->-]<--.>+++++++[<
++++++++++>-]<+++.+++++++++++.>++++++++[<----------->-]<++++
.>+++++[<+++++++++++++>-]<.>+++[<++++++>-]<-.---.++++++.----
---.----------.>++++++++[<----------->-]<+.---.[-]<<<->[-]>[
-]<<[>+>+<<-]>>[<<+>>-]>>>[-]<<<+++++++++<[>>>+<<[>+>[-]<<-]
>[<+>-]>[<<++++++++++>>>+<-]<<-<-]+++++++++>[<->-]>>+>[<[-]<
<+>>>-]>[-]+<<[>+>-<<-]<<<[>>+>+<<<-]>>>[<<<+>>>-]<>>[<+>-]<
<-[>[-]<[-]]>>+<[>[-]<-]<++++++++[<++++++<++++++>>-]>>>[>+>+
<<-]>>[<<+>>-]<[<<<<<.>>>>>-]<<<<<<.>>[-]>[-]++++[<++++++++>
-]<.>++++[<++++++++>-]<++.>+++++[<+++++++++>-]<.><+++++..---
-----.-------.>>[>>+>+<<<-]>>>[<<<+>>>-]<[<<<<++++++++++++++
.>>>>-]<<<<[-]>++++[<++++++++>-]<.>+++++++++[<+++++++++>-]<-
-.---------.>+++++++[<---------->-]<.>++++++[<+++++++++++>-]
<.+++..+++++++++++++.>++++++++[<---------->-]<--.>+++++++++[
<+++++++++>-]<--.-.>++++++++[<---------->-]<++.>++++++++[<++
++++++++>-]<++++.------------.---.>+++++++[<---------->-]<+.
>++++++++[<+++++++++++>-]<-.>++[<----------->-]<.+++++++++++
..>+++++++++[<---------->-]<-----.---.+++.---.[-]<<<]
"""

bf = Brainfuck()
#bf.SetProgram( bf_locking )
bf.SetProgram( bf_99beer )
bf.Run()
