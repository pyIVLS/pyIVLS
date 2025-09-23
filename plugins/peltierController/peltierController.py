"""
This is a class for peltier controller

"""

import serial
from threading import Lock


class peltierController:
    def __init__(self):
        self.device = serial.Serial()  # https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        self.device.baudrate = 115200
        self.device.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.device.parity = serial.PARITY_NONE  # set parity check: no parity
        self.device.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self.device.writeTimeout = 2  # just to make sure that there will be enough time if there will be overlapping operations

        self.lock = Lock()

    def open(self, source=None):
        """Opens the port of peltier controller

        Returns [status, message]:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        if source is None:
            return [1, "source address is None"]
        if self.device.is_open:
            return [0, "device is already connected"]
        else:
            try:
                with self.lock:
                    self.device.port = source
                    self.device.open()
                    self.device.reset_input_buffer()
                    self.device.reset_output_buffer()
                    self.device.write("SETP 0\r".encode())
                return [0, "device connected"]
            except serial.SerialException:
                return [4, "can not connect the device"]

    def close(self):
        """close the port of peltier controller

        Returns [status, message]:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        if not (self.device.is_open):
            return [0, "device is not connected"]
        else:
            try:
                with self.lock:
                    self.device.write("SETP 0\r".encode())
                    self.device.reset_input_buffer()
                    self.device.reset_output_buffer()
                    self.device.close()
                return [0, "device disconnected"]
            except serial.SerialException:
                return [4, "can not disconnect the device"]

    def setT(self, temperature):
        """set the setpoint

        Returns [status, message]:
            0 - no error
            ~0 - error (add error code later on if needed)

        """
        try:
            with self.lock:
                self.device.write(f"SETT {temperature}\r".encode())
            return [0, "temperature set"]
        except serial.SerialException:
            return [4, "error setting the temperature"]

    def setP(self, power):
        """set the power

        Returns [status, message]:
            0 - no error
            ~0 - error (add error code later on if needed)

        """
        try:
            with self.lock:
                self.device.write(f"SETP {power}\r".encode())
            return [0, "power set"]
        except serial.SerialException:
            return [4, "error setting the power"]

    def setPID(self, kp, ki, kd):
        """set the power

        Returns [status, message]:
            0 - no error
            ~0 - error (add error code later on if needed)

        """
        try:
            with self.lock:
                self.device.write(f"SETKP {kp}\r".encode())
                self.device.write(f"SETKI {ki}\r".encode())
                self.device.write(f"SETKD {kd}\r".encode())
            return [0, "PID parameters set"]
        except serial.SerialException:
            return [4, "error setting PID parameters"]

    def getData(self):
        """get the data out of controller and return it in a form of dict

        Returns [status, dict/message if error]:
            0 - no error
            ~0 - error (add error code later on if needed)

        dict['info'] - full output
        dict['T'] - temperature (float)
        NOTE: other values may be added to dict later
        """
        dataOrder = [
            "",
            "Setpoint:",
            "T1:",
            "T2:",
            "T1_ref:",
            "T2_ref:",
            "actionasnum",
            "action",
            "mode",
            "kp=",
            "ki=",
            "kd=",
            "lowlimit=",
            "highlimit=",
            "menu=",
            "rota=",
            "power=",
            "power=",
            "",
        ]
        numericValues = [
            1,
            2,
            3,
            4,
            5,
            6,
            9,
            10,
            11,
            12,
            13,
            14,
            16,
        ]  # %what numeric values should be extracted dataOutput
        stringValues = [
            7,
            8,
            15,
            17,
        ]  # %what string values should be extracted from dataOutput
        dataOutput = {}
        dataOutput["raw"] = ""
        try:
            with self.lock:
                self.device.write(" \r".encode())
                for cnt, _ in enumerate(dataOrder):
                    response = self.device.readline().decode("utf-8")
                    if len(dataOrder[cnt]) < 1:
                        continue
                    if dataOrder[cnt][-1] not in [":", "="]:
                        dict_key = dataOrder[cnt]
                    else:
                        dict_key = dataOrder[cnt][0:-1]
                    dataOutput["raw"] = dataOutput["raw"] + response[1:-1] + "\n"
                    if cnt in numericValues:
                        if response[len(dataOrder[cnt]) + 1 : -1] == "na":
                            dataOutput[dict_key] = float("nan")
                        else:
                            dataOutput[dict_key] = float(response[len(dataOrder[cnt]) + 1 : -1])
                    if cnt in stringValues:
                        dataOutput[dict_key] = response[len(dataOrder[cnt]) : -1]
            return [0, dataOutput]
        except serial.SerialException:
            return [4, "error in communication with device"]
        except ValueError:
            return [1, "error in data from the device"]
