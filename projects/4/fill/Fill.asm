// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
(WHITESCREEN)
    @color
    M=0
(LOOP)
    // screenTarget = @SCREEN
    @SCREEN
    D=A
    @screenTarget
    M=D
    // row = 256
    @256
    D=A
    @row
    M=D
    // i = 1
    @i
    M=1
// fill screen by color
(LOOPROW)
    // if (i > row) goto STOPROW
    @i
    D=M
    @row
    D=D-M
    @STOPROW
    D;JGT
    // col = 32 (512 / 16)
    @32
    D=A
    @col
    M=D
    // j = 1
    @j
    M=1
(LOOPCOL)
    // if (j > col) goto STOPCOL
    @j
    D=M
    @col
    D=D-M
    @STOPCOL
    D;JGT
    // paint screen target
    // @screenTarget = color
    @color
    D=M
    @screenTarget
    A=M
    M=D
    // screenTarget = screenTarget + 1
    @screenTarget
    M=M+1
    // j = j + 1
    @j
    M=M+1
    // goto LOOPCOL
    @LOOPCOL
    0;JMP
(STOPCOL)
    // i = i + 1
    @i
    M=M+1
    // goto LOOPROW
    @LOOPROW
    0;JMP
(STOPROW)
    // fill screen to white if no keys are pressed
    @KBD
    D=M
    @WHITESCREEN
    D;JEQ
    // fill screen to black
    @color
    M=-1
    @LOOP
    0;JMP
(END)
    @END
    0;JMP
