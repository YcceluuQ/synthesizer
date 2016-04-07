import time
from rhythmbox import Output, Sample
from synth import WaveSynth, key_freq, Oscillator, SimpleOscillator
from collections import OrderedDict

# some note frequencies for octaves 1 to 7
octave_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes1 = OrderedDict((note, key_freq(4+i)) for i, note in enumerate(octave_notes))
notes2 = OrderedDict((note, key_freq(16+i)) for i, note in enumerate(octave_notes))
notes3 = OrderedDict((note, key_freq(28+i)) for i, note in enumerate(octave_notes))
notes4 = OrderedDict((note, key_freq(40+i)) for i, note in enumerate(octave_notes))
notes5 = OrderedDict((note, key_freq(52+i)) for i, note in enumerate(octave_notes))
notes6 = OrderedDict((note, key_freq(64+i)) for i, note in enumerate(octave_notes))
notes7 = OrderedDict((note, key_freq(76+i)) for i, note in enumerate(octave_notes))


def demo_tones():
    synth = WaveSynth()
    with Output(nchannels=1) as out:
        for wave in [synth.square_h, synth.square, synth.sine, synth.triangle, synth.sawtooth, synth.sawtooth_h]:
            print(wave.__name__)
            for note, freq in notes4.items():
                print("   {:f} hz".format(freq))
                sample = wave(freq, duration=0.4).fadein(0.02).fadeout(0.1)
                out.play_sample(sample)
        print("pulse")
        for note, freq in notes4.items():
            print("   {:f} hz".format(freq))
            sample = synth.pulse(freq, duration=0.4, pulsewidth=0.1).fadein(0.02).fadeout(0.1)
            out.play_sample(sample)
        print("harmonics (only even)")
        for note, freq in notes3.items():
            print("   {:f} hz".format(freq))
            sample = synth.harmonics(freq, duration=0.4, num_harmonics=5, only_odd=True).fadein(0.02).fadeout(0.1)
            out.play_sample(sample)
        print("noise")
        sample = synth.white_noise(duration=1.5).fadein(0.1).fadeout(0.1)
        out.play_sample(sample)


def demo_song():
    synth = WaveSynth()
    notes = {note: key_freq(49+i) for i, note in enumerate(['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'])}
    tempo = 0.3

    def instrument(freq, duration):
        a = synth.harmonics(freq, duration, num_harmonics=4, amplitude=0.8, only_even=True)
        return a.envelope(0.05, 0.2, 0.8, 0.5)

    print("Synthesizing tones...")
    quarter_notes = {note: instrument(notes[note], tempo) for note in notes}
    half_notes = {note: instrument(notes[note], tempo*2) for note in notes}
    full_notes = {note: instrument(notes[note], tempo*4) for note in notes}
    song = "A A B. A D. C#.. ;  A A B. A E. D.. ;  A A A. F#.. D C#.. B ;  G G F#.. D E D ; ; "\
        "A A B. A D C#.. ; A A B. A E D. ; A A A. F#.. D C#.. B ; G G F#.. D E D ; ; "
    with Output(synth.samplerate, synth.samplewidth, 1) as out:
        for note in song.split():
            if note == ";":
                print()
                time.sleep(tempo*2)
                continue
            print(note, end="  ", flush=True)
            if note.endswith(".."):
                sample = full_notes[note[:-2]]
            elif note.endswith("."):
                sample = half_notes[note[:-1]]
            else:
                sample = quarter_notes[note]
            out.play_sample(sample)
        print()


def demo_plot():
    from matplotlib import pyplot as plot
    plot.title("Various waveforms")
    synth = WaveSynth(samplerate=1000)
    freq = 4
    s = synth.sawtooth(freq, duration=1)
    plot.plot(s.get_frame_array())
    s = synth.sine(freq, duration=1)
    plot.plot(s.get_frame_array())
    s = synth.triangle(freq, duration=1)
    plot.plot(s.get_frame_array())
    s = synth.square(freq, duration=1)
    plot.plot(s.get_frame_array())
    s = synth.square_h(freq, duration=1)
    plot.plot(s.get_frame_array())
    s = synth.pulse(freq, duration=1, pulsewidth=0.2)
    plot.plot(s.get_frame_array())
    plot.show()


def modulate_amp():
    from matplotlib import pyplot as plot
    synth = WaveSynth()
    freq = 220
    s1 = synth.triangle(freq, duration=2)
    m = synth.sine(2, duration=2, amplitude=0.4, bias=0.5)
    s1.modulate_amp(m)
    plot.title("Amplitude modulation by another waveform")
    plot.plot(s1.get_frame_array())
    plot.show()
    with Output(nchannels=1) as out:
        out.play_sample(s1)
    s1 = synth.triangle(freq, duration=2)
    m = synth.oscillator.sine(3, amplitude=0.4, bias=0.5)
    s1.modulate_amp(m)
    plot.title("Amplitude modulation by an oscillator")
    plot.plot(s1.get_frame_array())
    plot.show()
    with Output(nchannels=1) as out:
        out.play_sample(s1)


def envelope():
    from matplotlib import pyplot as plot
    synth = WaveSynth()
    freq = 440
    s = synth.triangle(freq, duration=1)
    s.envelope(0.05, 0.1, 0.2, 0.4)
    plot.title("ADSR envelope")
    plot.plot(s.get_frame_array())
    plot.show()
    with Output(nchannels=1) as out:
        out.play_sample(s)


def fm():
    synth = WaveSynth(samplerate=8000)
    from matplotlib import pyplot as plot
    freq = 2000
    lfo1 = synth.oscillator.sine(1, amplitude=0.4)
    s1 = synth.sine(freq, duration=3, fm_lfo=lfo1)
    plot.title("Spectrogram")
    plot.ylabel("Freq")
    plot.xlabel("Time")
    plot.specgram(s1.get_frame_array(), Fs=synth.samplerate, noverlap=90, cmap=plot.cm.gist_heat)
    plot.show()
    with Output(nchannels=1, samplerate=22050) as out:
        synth = WaveSynth(samplerate=22050)
        freq = 440
        lfo1 = synth.oscillator.linear(5)
        lfo1 = synth.oscillator.envelope(lfo1, 1, 0.5, 0.5, 0.5, 1)
        s1 = synth.sine(freq, duration=3, fm_lfo=lfo1)
        s_all = s1.copy()
        out.play_sample(s1)
        lfo1 = synth.oscillator.sine(1, amplitude=0.2)
        s1 = synth.sine(freq, duration=2, fm_lfo=lfo1)
        s_all.join(s1)
        out.play_sample(s1)
        lfo1 = synth.oscillator.sine(freq/17, amplitude=0.5)
        s1 = synth.sine(freq, duration=2, fm_lfo=lfo1)
        s_all.join(s1)
        out.play_sample(s1)
        lfo1 = synth.oscillator.sine(freq/6, amplitude=0.5)
        s1 = synth.sine(freq, duration=2, fm_lfo=lfo1)
        s_all.join(s1)
        out.play_sample(s1)
        lfo1 = synth.oscillator.sine(1, amplitude=0.4)
        s1 = synth.triangle(freq, duration=2, fm_lfo=lfo1)
        s_all.join(s1)
        out.play_sample(s1)
        freq = 440*2
        lfo1 = synth.oscillator.sine(freq/80, amplitude=0.4)
        s1 = synth.triangle(freq, duration=2, fm_lfo=lfo1)
        s_all.join(s1)
        out.play_sample(s1)
        # s_all.write_wav("fmtestall.wav")


def pwm():
    from matplotlib import pyplot as plot
    synth = WaveSynth(samplerate=1000)
    pwm_lfo = synth.oscillator.sine(0.05, amplitude=0.49, bias=0.5)
    s1 = synth.pulse(4, amplitude=0.6, duration=20, pwm_lfo=pwm_lfo)
    plot.figure(figsize=(16, 4))
    plot.title("Pulse width modulation")
    plot.ylim([-35000, 35000])
    plot.plot(s1.get_frame_array())
    plot.show()
    with Output(nchannels=1) as out:
        synth = WaveSynth()
        lfo2 = synth.oscillator.sine(0.2, amplitude=0.48, bias=0.5)
        s1 = synth.pulse(440/6, amplitude=0.5, duration=6, fm_lfo=None, pwm_lfo=lfo2)
        out.play_sample(s1)
        # s1.write_wav("pwmtest.wav")


def oscillator():
    from matplotlib import pyplot as plot
    lfo = Oscillator(1000)
    l2 = lfo.square_h(4)
    plot.subplot(2, 1, 1)
    plot.title("Square from harmonics")
    plot.plot([next(l2) for _ in range(1000)])
    l3 = lfo.harmonics(4, 8, only_even=True)
    plot.subplot(2, 1, 2)
    plot.title("Even harmonics")
    plot.plot([next(l3) for _ in range(1000)])
    plot.show()


def bias():
    from matplotlib import pyplot as plot
    synth = WaveSynth(samplerate=1000)
    waves = []
    waves.append(synth.sine(2, 4, 0.02, bias=0.1))
    waves.append(synth.triangle(2, 4, 0.02, bias=0.2))
    waves.append(synth.pulse(2, 4, 0.02, bias=0.3, pulsewidth=0.45))
    waves.append(synth.harmonics(2, 4, 7, 0.02, bias=0.4))
    waves.append(synth.sawtooth(2, 4, 0.02, bias=0.5))
    waves.append(synth.sawtooth_h(2, 4, 7, 0.02, bias=0.6))
    waves.append(synth.square(2, 4, 0.02, bias=0.7))
    waves.append(synth.square_h(2, 4, 7, 0.02, bias=0.8))
    waves.append(synth.white_noise(4, amplitude=0.02, bias=0.9))
    for wave in waves:
        plot.plot(wave.get_frame_array())
    plot.title("All waveforms biased to levels above zero")
    plot.show()


def lfo_envelope():
    synth = WaveSynth(samplerate=100)
    lfo = synth.oscillator.linear(1000)
    lfo = synth.oscillator.envelope(lfo, 2, 1, 4, 0.3, 2, stop_at_end=True)
    from matplotlib import pyplot as plot
    plot.title("LFO Envelope")
    plot.plot(list(lfo))
    plot.show()


def a440():
    synth = WaveSynth(samplerate=44100, samplewidth=4)
    a440 = synth.sine(440, duration=3)
    with Output.for_sample(a440) as out:
        out.play_sample(a440)


def echo_sample():
    synth = WaveSynth(samplerate=22050)
    lfo = synth.oscillator.linear(1, -0.0001)
    s = synth.pulse(220, .5, fm_lfo=lfo).fadeout(.2)
    with Output(s.samplerate, s.samplewidth, s.nchannels) as out:
        e = s.copy().echo(1, 4, 0.5, 0.4)   # echo
        out.play_sample(e)
        e = s.copy().echo(1, 30, 0.1, 0.5)    # reverberation
        out.play_sample(e)


def echo_lfo():
    synth = WaveSynth(22050)
    lfo = synth.oscillator
    s = lfo.sawtooth(440, amplitude=25000)
    s = lfo.envelope(s, 1, 0.1, 0, 0, 2, stop_at_end=True)
    s = lfo.echo(s, 0.8, 6, 0.3, 0.7)
    frames = [int(y) for y in s]
    import matplotlib.pyplot as plot
    plot.plot(frames)
    plot.show()
    samp = Sample.from_array(frames, synth.samplerate, 1)
    with Output.for_sample(samp) as out:
        out.play_sample(samp)


def lfo_func():
    rate = 1000
    synth = WaveSynth(rate)
    lfo = synth.oscillator
    s = lfo.sine(1, amplitude=100, bias=40)
    s = lfo.abs(s)
    s = lfo.clip(s, minimum=20, maximum=80)
    s = lfo.delay(s, 1)
    s = [next(s) for _ in range(rate*2)]
    import matplotlib.pyplot as plot
    a = plot.subplot(111)
    a.set_ylim([-50, 100])
    a.plot(s)
    plot.show()


def bells():
    def makebell(freq):
        synth = WaveSynth()
        duration = 2
        divider = 2.2823535
        fm = synth.oscillator.triangle(freq/divider, amplitude=0.5)
        s = synth.sine(freq, duration, fm_lfo=fm)
        # apply ADSR envelope that resembles bell amp curve, see http://www.hibberts.co.uk/make.htm
        s.envelope(0, duration*0.25, .5, duration*0.75)
        s.echo(2, 5, 0.06, 0.6)
        return s.make_32bit(False)
    b_l1 = makebell(key_freq(56))
    b_l2 = makebell(key_freq(60))
    b_h1 = makebell(key_freq(78)).amplify(0.7)
    b_h2 = makebell(key_freq(82)).amplify(0.7)
    b_h3 = makebell(key_freq(84)).amplify(0.7)
    bells = b_l1.mix_at(1.0, b_h1)
    bells.mix_at(1.5, b_h2)
    bells.mix_at(2, b_h3)
    bells.mix_at(3, b_l2)
    bells.mix_at(4, b_h2)
    bells.mix_at(4.5, b_h3)
    bells.mix_at(5, b_h1)
    bells.make_16bit()
    with Output.for_sample(bells) as out:
        out.play_sample(bells)


def stereo_pan():
    synth = WaveSynth()
    # panning a stereo source:
    wave = Sample("samples/SOS 020.wav").clip(6, 12).normalize().fadein(0.5).fadeout(0.5).lock()
    osc = synth.oscillator.sine(0.4)
    panning = wave.copy().pan(lfo=osc).fadeout(0.2)
    with Output.for_sample(panning) as out:
        out.play_sample(panning)
    # panning a generated mono source:
    fm = synth.oscillator.sine(0.5, 0.1999, bias=0.2)
    wave = synth.triangle(220, 5, fm_lfo=fm).lock()
    osc = synth.oscillator.sine(0.4)
    panning = wave.copy().pan(lfo=osc).fadeout(0.2)
    with Output.for_sample(panning) as out:
        out.play_sample(panning)


def osc_bench():
    rate = 44100
    lfo = Oscillator(rate)
    simple_lfo = SimpleOscillator(rate)
    duration = 2.0
    def get_values(osc):
        values = [next(osc) for _ in range(int(rate*duration))]
    fm = lfo.sine(220)
    print("GENERATING {:g} SECONDS SAMPLE DATA {:d} HZ USING LFO.".format(duration, rate))
    print("  WAVEFORM: with-FM / no-FM / optimized")
    # sine
    print("      Sine:   ", end="")
    start = time.time()
    get_values(lfo.sine(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.sine(440))
    duration2 = time.time()-start
    start = time.time()
    get_values(simple_lfo.sine(440))
    duration3 = time.time()-start
    print("{:.3f} / {:.3f} / {:.3f}".format(duration1, duration2, duration3))
    # triangle
    print("  Triangle:   ", end="")
    start = time.time()
    get_values(lfo.triangle(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.triangle(440))
    duration2 = time.time()-start
    start = time.time()
    get_values(simple_lfo.triangle(440))
    duration3 = time.time()-start
    print("{:.3f} / {:.3f} / {:.3f}".format(duration1, duration2, duration3))
    # square
    print("    Square:   ", end="")
    start = time.time()
    get_values(lfo.square(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.square(440))
    duration2 = time.time()-start
    start = time.time()
    get_values(simple_lfo.square(440))
    duration3 = time.time()-start
    print("{:.3f} / {:.3f} / {:.3f}".format(duration1, duration2, duration3))
    # sawtooth
    print("  Sawtooth:   ", end="")
    start = time.time()
    get_values(lfo.sawtooth(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.sawtooth(440))
    duration2 = time.time()-start
    start = time.time()
    get_values(simple_lfo.sawtooth(440))
    duration3 = time.time()-start
    print("{:.3f} / {:.3f} / {:.3f}".format(duration1, duration2, duration3))
    # pulse
    print("     Pulse:   ", end="")
    start = time.time()
    get_values(lfo.pulse(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.pulse(440))
    duration2 = time.time()-start
    start = time.time()
    get_values(simple_lfo.pulse(440))
    duration3 = time.time()-start
    print("{:.3f} / {:.3f} / {:.3f}".format(duration1, duration2, duration3))
    # square_h
    print("  Square_H:   ", end="")
    start = time.time()
    get_values(lfo.square_h(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.square_h(440))
    duration2 = time.time()-start
    print("{:.3f} / {:.3f}".format(duration1, duration2))
    print("Sawtooth_H:   ", end="")
    start = time.time()
    get_values(lfo.sawtooth_h(440, fm_lfo=fm))
    duration1 = time.time()-start
    start = time.time()
    get_values(lfo.sawtooth_h(440))
    duration2 = time.time()-start
    print("{:.3f} / {:.3f}".format(duration1, duration2))
    print("     Noise:   ", end="")
    start = time.time()
    get_values(lfo.white_noise())
    duration1 = time.time()-start
    print("        {:.3f}".format(duration1))
    print("    Linear:   ", end="")
    start = time.time()
    get_values(lfo.linear(0, 0.0001))
    duration1 = time.time()-start
    print("        {:.3f}".format(duration1))


def test_simple_osc():
    import itertools
    synth = WaveSynth(1000)
    w1 = synth.sine(10, 1)
    w2 = synth.sine(10, 1, fm_lfo=itertools.repeat(0.0))
    assert w1 == w2
    w1 = synth.triangle(10, 1)
    w2 = synth.triangle(10, 1, fm_lfo=itertools.repeat(0.0))
    assert w1 == w2
    w1 = synth.square(10, 1)
    w2 = synth.square(10, 1, fm_lfo=itertools.repeat(0.0))
    assert w1 == w2
    w1 = synth.sawtooth(10, 1)
    w2 = synth.sawtooth(10, 1, fm_lfo=itertools.repeat(0.0))
    assert w1 == w2
    w1 = synth.pulse(10, 1)
    w2 = synth.pulse(10, 1, fm_lfo=itertools.repeat(0.0))
    assert w1 == w2


def vibrato():
    synth = WaveSynth()
    duration = 3
    def make_sample(freq):
        fmfm = synth.oscillator.linear(0, 0.002)
        fm = synth.oscillator.sine(0.05, amplitude=0.5, fm_lfo=fmfm)
        s1 = synth.sawtooth(freq, duration, amplitude=0.6, fm_lfo=fm)
        s1.envelope(0.01, 0.1, 0.6, 2)
        return s1
    with Output(synth.samplerate, nchannels=1) as out:
        for f in [220, 330, 440]:
            sample = make_sample(f)
            out.play_sample(sample)


if __name__ == "__main__":
    test_simple_osc()
    osc_bench()
    lfo_func()
    bells()
    echo_sample()
    echo_lfo()
    demo_plot()
    a440()
    demo_tones()
    demo_song()
    modulate_amp()
    envelope()
    pwm()
    fm()
    oscillator()
    bias()
    lfo_envelope()
    stereo_pan()
    vibrato()
