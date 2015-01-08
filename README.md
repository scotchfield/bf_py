# Brainfuck with threads and assertions, written in Python.

Uses the standard eight  brainfuck commands and adds two:
- *: Initialize a program counter here operating in the same shared memory space. Moving outside the program or into another thread's space will terminate the specific process.
- !: Assert if the current memory at the pointer is non-zero.

# Why?
This was originally created as a way to transform Brainfuck to [BIR](http://bogor.projects.cis.ksu.edu/manual/ch02.html), which was used in the [Bogor model checking framework](http://bogor.projects.cis.ksu.edu/manual/).

# Why??
Great question! Because it's a threaded Brainfuck with assertions, I guess. Wacky..

