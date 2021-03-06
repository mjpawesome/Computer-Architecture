"""CPU functionality."""

import sys

#instruction codes
LDI = 130
PRN = 71
HLT = 1
MUL = 162
ADD = 160
PUSH = 69
POP = 70
RET = 17
CALL = 80
CMP = 167
JMP = 84
JEQ = 85
JNE = 86

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ir = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.SP = self.reg[7]
        self.flag = 0B00000000

    # MAR = Memory address    
    def ram_read(self, MAR):
        return self.ram[MAR]

    # MDA = Memory Data
    def ram_write(self, MAR, MDA):
        self.ram[MAR] = MDA
        return self.ram[MAR]

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []

        if len(sys.argv) != 2:  
            print("usage invalid")
            sys.exit(1)

        try:
            with open(f'examples/{sys.argv[1]}') as f:
                for line in f:
                    try:
                        line = line.split('#', 1)[0]
                        line = int(line, 2)          
                        program.append(line)
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(2)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            # Instruction Register - internal part of CPU that holds a value.  Special purpose part of CPU.
            ir = self.ram[self.pc] 

            # Set the value of a register to an integer.
            if ir == LDI: 
                reg_num = self.ram_read(self.pc+1)
                value = self.ram_read(self.pc+2)
                self.reg[reg_num] = value
                self.pc += 3 
            
            # Print numeric value stored in the given registe
            elif ir == PRN: 
                reg_num = self.ram_read(self.pc+1)
                print(self.reg[reg_num])
                self.pc += 2

            # Halt the CPU (and exit the emulator).
            elif ir == HLT: 
                running = False

            # Multiply the values in two registers together and store the result in registerA
            elif ir == MUL: 
                num1 = self.ram_read(self.pc+1)
                num2 = self.ram_read(self.pc+2)
                self.alu("MUL", num1, num2)
                self.pc += 3

            # Add the value in two registers and store the result in registerA.
            elif ir == ADD:
                num1 = self.ram_read(self.pc+1)
                num2 = self.ram_read(self.pc+2)
                self.alu("ADD", num1, num2)
                self.pc += 3

            # Push the value in the given register on the stack.
            elif ir == PUSH: 
                self.SP -= 1 # decriment SP (stack pointer)
                reg_num = self.ram_read(self.pc + 1)   # get value from register
                value = self.reg[reg_num] # we want to push this value
                top_of_stack_addr = self.SP # get top of stack address
                self.ram[top_of_stack_addr] = value # store value at top of the stack
                self.pc += 2 # increment PC

            # Pop the value at the top of the stack into the given register.
            elif ir == POP: 
                top_of_stack_addr = self.SP
                reg_num = self.ram_read(self.pc+1)
                self.reg[reg_num] = self.ram[top_of_stack_addr]
                self.SP += 1
                self.pc += 2

            # Pop the value from the top of the stack and store it in the PC
            elif ir == RET: # RET
                self.pc = self.ram_read(self.SP)
                self.SP += 1

            # Calls a subroutine (function) at the address stored in the register.
            elif ir == CALL:
                self.SP -= 1 # decriment SP (stack pointer)         
                self.ram[self.SP] = self.pc + 2 # push address of next instruction onto the stack
                reg_num = self.ram_read(self.pc + 1)  # get reg_num from memory
                self.pc = self.reg[reg_num] # set the pc

            # Compare the values in two registers.
            elif ir == CMP:
                op_a = self.ram_read(self.pc+1)
                op_b = self.ram_read(self.pc+2)
                self.alu("CMP", op_a, op_b)
                self.pc += 3

            # Jump to the address stored in the given register.
            elif ir == JMP:
                # get address from register
                reg_num= self.ram_read(self.pc+1)
                # set pc to address
                self.pc = self.reg[reg_num]

            # If equal flag is set (true), jump to the address stored in the given register.
            elif ir == JEQ:
                if self.flag == 0b00000001:
                    reg_num = self.ram_read(self.pc+1)
                    self.pc = self.reg[reg_num]
                else:
                    self.pc += 2  

            # If E flag is clear (false, 0), jump to the address stored in the given register.
            elif ir == JNE:
                if self.flag != 0b00000001:
                    reg_num = self.ram_read(self.pc+1)
                    self.pc = self.reg[reg_num]
                else:
                    self.pc += 2      

            else:
                self.pc += 1

 
    # x >> 6 is right shift by 6
    # x << 6 is left shift by 6


    

