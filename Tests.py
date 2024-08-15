import pyvisa

if __name__ == "__main__":
    keithley_name = "TCPIP::192.168.1.5::INSTR"
    rm = pyvisa.ResourceManager("@py")
    k = rm.open_resource(keithley_name)
    print(k.query("*IDN?"))
    k.close()
