"""CPU functionality."""

import sys

SP = 7
HLT = 0b1

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4 # Set the stack pointer (SP) to 244 -
        self.pc = 0 # Program Counter (PC), the index into memory of the currently-executing instruction
        self.flags = 0b0
        self.hlt: HLT # Hault

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
                        line = line.split('#', 1)[0].strip()
                        if line:
                            line = int(line, 2)
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
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = 0b10
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags = 0b100
        elif op == 'AND':
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == 'NOT':
            reg = self.reg[reg_a]
            value = self.reg[reg]
            self.reg[reg] = ~value
        elif op == 'SHL':
            # SHL - SHift Left
            self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            # SHR - SHift Right
            self.reg[reg_a] >> self.reg[reg_b]
        elif op == 'MOD':
            if self.reg[reg_b] == 0:
                print('Can not perform MOD on 0 value.')
                self.hlt(reg_a, reg_b)
            else: self.reg[reg_a] %= self.reg[reg_b]
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
            0b10100010: 'MUL',
            0b10100000: 'ADD',
            0b01000101: 'PUSH',
            0b01000110: 'POP',
            0b01010000: 'CALL',
            0b00010001: 'RET',
            0b10100111: 'CMP',
            0b01010100: 'JMP',
            0b01010101: 'JEQ',
            0b01010110: 'JNE',
            0b10101000: 'AND',
            0b10101010: 'OR',
            0b10101011: 'XOR',
            0b01101001: 'NOT',
            0b10101100: 'SHL',
            0b10101101: 'SHR',
            0b10100100: 'MOD'
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
            elif ins == 'ADD':
                # Preform MUL Action.
                reg_num_a = self.ram_read(self.pc + 1)
                reg_num_b = self.ram_read(self.pc + 2)
                self.reg[reg_num_a] += self.reg[reg_num_b]
                self.pc += 3
            elif ins == 'PUSH':
                # Push to the stack stored in RAM.

                # Decrement the stack pointer.
                self.reg[SP] -= 1
                self.reg[SP] &= 0xff

                # Get the number to be stored in the stack.
                register_number = self.ram_read(self.pc + 1)
                value = self.reg[register_number] 

                # Store address to save at and then store it.
                save_addr = self.reg[SP]
                self.ram[save_addr] = value

                self.pc += 2
            elif ins == 'POP':
                # Push to the stack stored in RAM.
                
                # Store address to pop and the value of the pop'd item.
                addr = self.reg[SP]
                value = self.ram[addr]

                register_number = self.ram[self.pc + 1]
                self.reg[register_number] = value

                self.reg[SP] += 1
                self.pc += 2
            elif ins == 'CALL':
                from_addr = self.pc + 2
                
                self.reg[SP] -= 1 # Decrement stack pointer by 1.
                
                to_addr = self.reg[SP]
                
                self.ram[to_addr] = from_addr
                
                register_number = self.ram[self.pc + 1]
                subroute_addr = self.reg[register_number]
                
                self.pc = subroute_addr
            elif ins == 'RET':
                from_addr = self.reg[SP]
                return_addr = self.ram[from_addr]
                self.reg[SP] += 1
                self.pc = return_addr
            elif ins == 'CMP':
                # Compare the values in two registers. | ### CMP Line 224 in Spec
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                
                self.alu('CMP', reg_a, reg_b)
                self.pc += 3
            elif ins == 'JMP':
                # Jump to the address stored in the given register. | ### JMP Line 407 in Spec
                reg_a = self.ram[self.pc + 1] # STore location to jump to.
                self.pc = self.reg[reg_a] # Set the pointer to the jump location.
                return True
            elif ins == 'JEQ':
                # If `equal` flag is set (true), jump to the address stored in the given register. | ### JEQ Line 345 in Spec
                reg_a = self.ram[self.pc + 1] # Pointer to jump to if flag is True
                if (self.flags & 0b1) == 1:
                    self.pc = self.reg[reg_a]
                else:
                    # Skip over because flag is not True
                    self.pc += 2
            elif ins == 'JNE':
                # If `E` flag is clear (false, 0), jump to the address stored in the given register. | ### JNE Line 422 in Spec
                reg_a = self.ram[self.pc + 1] # Address to jump to.
                if (self.flags & 0b1) == 0:
                    self.pc = self.reg[reg_a]
                else:
                    # Skip over because flag is not False
                    self.pc += 2

            # -----------------------------
            # ---------- Stretch ----------
            # -----------------------------
            elif ins == 'AND' or ins == 'OR' or ins == 'XOR' or ins == 'NOT'
                    or ins == 'SHL' or ins == 'SHR' or ins == 'MOD':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu(ins, reg_a, reg_b)
                self.pc += 3
            else: print(f'Unknown Instruction Code: {i}')