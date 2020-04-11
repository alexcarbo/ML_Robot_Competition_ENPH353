import anki_vector as av

def main():
    ANKI_SERIAL = '006046ca'
    ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY

    with av.Robot(serial=ANKI_SERIAL,
        behavior_control_level=ANKI_BEHAVIOR) as robot:
        # robot.audio.stream_wav_file('/home/fizzer/.anki_vector/Lab4/1.wav')
        print("Say 'Hello World'...")
        robot.behavior.say_text("a b c d e f g h i j k l m n o p q r s t u v w x y z")

if __name__ == "__main__":
    main()
