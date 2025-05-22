from serial.tools import list_ports
def main():
    for port in list_ports.grep(""):
        print(port.vid, port.description, port.device, port.pid)

if __name__ == "__main__":
    main()
