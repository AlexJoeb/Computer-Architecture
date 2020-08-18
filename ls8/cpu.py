"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # Program Counter (PC), the index into memory of the currently-executing instruction
        

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR): # Memory Address Register (MAR) / Memory Data Register (MDR)
        self.ram[MAR] = MDR

    def ram_clear(self): self.ram = [0] * 256

    def load(self, args=sys.argv[1:]):
        """Load a program into memory."""

        address = 0
        
        if len(args) < 1:
            print("Error: No file name provided.")
            return
        
        if not args[0] or args[0].split('.')[1] != 'ls8':
            print("Error: File not found. Only 'ls8' files accepted.")
            return

        try:
            with open(args[0]) as file:
                for line in file:
                    try:
                        line = int(line.split('#')[0].strip(), 2)
                        self.ram_write(address, line)
                        address += 1
                    except ValueError:
                        print("Error: Unknown value fed into RAM.")
                        return
        except ValueError:
            print("Error: Could not find and/or traverse file provided.")
            return

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

        ir = {
            0b10000010: 'LDI',
            0b01000111: 'PRN',
            0b00000001: 'HLT',
            0b10100010: 'MUL'
        }

        while running:
            i = self.ram[self.pc]
            ins = ir[i]
            if ins == 'LDI':
                # Preform LDI Action.
                reg_num = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)
                self.reg[reg_num] = value
                self.pc += 3
            elif ins == 'PRN':
                # Preform PRN Action.
                reg_num = self.ram_read(self.pc + 1)
                print(f'PRN > {self.reg[reg_num]}')
                self.pc += 2
            elif ins == 'HLT':
                # Preform HLT.
                running = False
            elif ins == 'MUL':
                # Preform MUL Action.
                reg_num_a = self.ram_read(self.pc + 1)
                reg_num_b = self.ram_read(self.pc + 2)
                self.reg[reg_num_a] *= self.reg[reg_num_b]
                self.pc += 3
            else: print(f'Unknown Instruction Code: {i}')