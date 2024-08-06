from supriya import Envelope, synthdef, Server
from supriya.ugens import EnvGen, Out, SinOsc
import time

sc = Server().boot(input_bus_channel_count=0)

@synthdef()
def simple_sine(frequency=440, amplitude=0.1, gate=1):
    sine = SinOsc.ar(frequency=frequency) * amplitude
    envelope = EnvGen.kr(envelope=Envelope.adsr(), gate=gate, done_action=2)
    Out.ar(bus=0, source=[sine * envelope] * 2)

# Define the frequency range for CPU activity
MIN_FREQUENCY = 220  # A3
MAX_FREQUENCY = 880  # A5
def map_cpu_to_frequency(cpu_usage):
    # Map the CPU usage percentage to a frequency within the specified range
    return MIN_FREQUENCY + (MAX_FREQUENCY - MIN_FREQUENCY) * (cpu_usage / 100.0)

def play_sound(frequency):
    print(f"Playing sound at frequency: {frequency}")

def play_ping():
    sc.add_synthdefs(simple_sine)
    sc.sync()
    group = sc.add_group()
    for i in range(3):
        _ = group.add_synth(simple_sine, frequency=222 * (i + 1))
    
    time.sleep(1)
    for synth in group.children[:]:
        synth.free()

def play_welcome():
    sc.add_synthdefs(simple_sine)
    sc.sync()
    group = sc.add_group()
    for i in range(3):
        _ = group.add_synth(simple_sine, frequency=111 * (i + 1))
    
    time.sleep(1)
    for synth in group.children[:]:
        synth.free()