
from pydub import AudioSegment

import src.config as config

import itertools
import os
import csv
import time
# stat -c
#  %Y webrtc_core.cc

def get_file(folder_path):
    file_list = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_list.append(file_path)
    return file_list

def get_mix(file1, offset1, file2, offset2, mix_file):
    sound1 = AudioSegment.from_file(file1, format="raw", frame_rate=16000, 
                            channels=1, sample_width=2)
    sound2 = AudioSegment.from_file(file2, format="raw", frame_rate=16000, 
                            channels=1, sample_width=2)
    sound1 = sound1- offset1
    sound2 = sound2- offset2
    mixed_sound = sound1.overlay(sound2)
    mixed_sound.export(mix_file, format="raw")

def get_mixed_name(voice, offset1, noise, offset2):
    return f"{os.path.basename(voice)}_{str(offset1)}_{os.path.basename(noise)}_{str(offset2)}.pcm"

def get_mixed_music_list():

    noise_dir = r"D:\Users\USER\Desktop\flowing\test_data\noise"
    voice_dir = r"D:\Users\USER\Desktop\flowing\test_data\talk_voice"
    mixed_dir = r"D:\Users\USER\Desktop\flowing\test_data\mix_voice"

    voice_li = get_file(voice_dir)
    noise_li = get_file(noise_dir)
    mix_product = list(itertools.product(voice_li, noise_li))
    for voice, noise in mix_product:
        for offset in range(0, 18, 6):
            get_mix(voice, 0, noise, offset, 
                    os.path.join(mixed_dir, get_mixed_name(voice, 0, noise, offset))
            )

def src_to_mix():
    noise_dir = r"D:\Users\USER\Desktop\flowing\test_data\noise"
    voice_dir = r"D:\Users\USER\Desktop\flowing\test_data\talk_voice"
    mixed_dir = r"D:\Users\USER\Desktop\flowing\test_data\mix_voice"

    voice_li = get_file(voice_dir)
    noise_li = get_file(noise_dir)
    out_li = []
    
    mix_product = list(itertools.product(voice_li, noise_li))
    for voice, noise in mix_product:
        for offset in range(0, 18, 6):
            mixed_file = os.path.join(mixed_dir, get_mixed_name(voice, 0, noise, offset))
            # print(voice, 0, noise, -offset, 
            #         os.path.join(mixed_dir, get_mixed_name(voice, 0, noise, offset))
            #     )
            out_li.append((voice, mixed_file))
    return out_li

def write_to_csv(data, file_path):
    with open(file_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in data:
            writer.writerow(row)

def count_mse(pcm_file1, pcm_file2):
    import numpy as np
    from scipy.fft import fft
    from scipy.spatial.distance import cosine

    # 读取PCM文件并转换为AudioSegment对象
    pcm_array1 = np.fromfile(pcm_file1, dtype=np.int16)
    pcm_array2 = np.fromfile(pcm_file2, dtype=np.int16)

    # 计算均方误差
    if len(pcm_array1) != len(pcm_array2):
        if len(pcm_array1) > len(pcm_array2):
            pcm_array1 = pcm_array1[:len(pcm_array2)]
        else:
            pcm_array2 = pcm_array2[:len(pcm_array1)]
        # raise ValueError("PCM files should have the same length.")
    squared_diff = np.square(pcm_array1 - pcm_array2)
    mse = np.mean(squared_diff)

    # 执行FFT变换获取频谱
    spectrum1 = np.abs(fft(pcm_array1))
    spectrum2 = np.abs(fft(pcm_array2))

    # 计算余弦相似度
    similarity = 1 - cosine(spectrum1, spectrum2)

    return mse, similarity

def test_mse():
    file = r"D:\Users\USER\Desktop\flowing\test_data\talk_voice\chinese_16k.pcm"
    print(file, file, count_mse(file, file))

def test():
    from paramiko import SSHClient, AutoAddPolicy, SFTP

    from src.adb_connector import AdbCnet
    android = AdbCnet("192.168.121.36")
    if not android.connect():
        exit(1)
    android.pwd = '/data/bin'
    linux = SSHClient()
    linux.set_missing_host_key_policy(AutoAddPolicy())
    linux.connect(hostname="192.168.121.88", 
                   username='lxb')
    linux.workplace = './Symbol'

    webrtc_path = r"/home/lxb/tool/sourcecode_libs_software_prebuilt_source/webrtc_aec3/src/main/jni/webrtc_core"
    play_path = r"~/warehouse_rv1106/sourcecode/servers/task/voice_play"
    bin_path = r"/home/lxb/warehouse_rv1106/build_tools/output/bin"

    android_lib_path = r"/oem/lib"

    
    workplace = r"D:\Users\USER\Desktop\flowing\MakePlusTemp"
    os.chdir(workplace)

    src_to_mix_li = src_to_mix()

    stdin, stdout, stderr = linux.exec_command(rf'cd {webrtc_path} && make -f Makefile.rv1106l')
    exit_status = stdout.channel.recv_exit_status()
    stdin, stdout, stderr = linux.exec_command('cd {play_path} && ./build_cmake.sh')
    exit_status = stdout.channel.recv_exit_status()
    
    with  linux.open_sftp() as sftp:
        sftp.get(rf'{webrtc_path}/libwebrtc_core.so', rf'{workplace}\libwebrtc_core.so')
        sftp.get(rf'{bin_path}/voice_play', rf'{workplace}\voice_play')
        sftp.close()
        android.push(rf'{workplace}\libwebrtc_core.so', android_lib_path)
        android.push(rf'{workplace}\voice_play', "/data/bin")
        android.run(rf'chmod', "777", '/data/bin/voice_play')

    pcm_dir = "/data/pcm"
    bin_file = rf"/data/bin/voice_play"
    rtc_dir = r"D:\Users\USER\Desktop\flowing\test_data\rtc_voice"
    result_li = []
    for src, mixed in src_to_mix_li:
        name = os.path.basename(mixed)
        rtc_name = rf"{name}_rtc.pcm"
        remote_path = rf"{pcm_dir}/{name}"
        remote_rtc_path = rf"{pcm_dir}/{rtc_name}"
        local_rtc_file = os.path.join(rtc_dir, rtc_name)
        android.push(mixed, pcm_dir)
        android.shell(bin_file, remote_path, remote_rtc_path, "&>", "log.txt")
        android.pull(remote_rtc_path, rtc_dir)
        print(src, local_rtc_file, count_mse(src, local_rtc_file))
        result_li.append([src, local_rtc_file, count_mse(src, local_rtc_file)])

    write_to_csv(result_li, rf"D:\Users\USER\Desktop\flowing\test_data\result_{time.time()}.csv")




def make_test():
    from .make_style import make_style_decorate
    from .file import UFile
    from .adb_connector import AdbCnet
    from .linux_controler import Linux
    from .localhost import LocalHost

    # cp(UFile(local, r"result1.xlsx"), UFile(local, r"result.xlsx"))
    # cp(UFile(linux, r"/home/lxb/Symbol/result1.xlsx"), UFile(local, r"result1.xlsx"))
    # android.pwd = r"/data"
    # cp(UFile(android, r"./result3.xlsx"), UFile(linux, r"/home/lxb/Symbol/result1.xlsx"))
    # cp(UFile(local, r"result3.xlsx"), UFile(android, r"./result3.xlsx"))

    @make_style_decorate
    def cp(target:UFile, src:UFile):
        import shutil
        nonlocal local
        print(f"{src} to {target}")
        if isinstance(target.RemoteUser, LocalHost) and isinstance(src.RemoteUser, LocalHost):
            shutil.copyfile(src.get_abs_path(), target.get_abs_path())
        elif not isinstance(src.RemoteUser, LocalHost):
            path = src.get_abs_path()
            if isinstance(target.RemoteUser, LocalHost):
                temp_path = target.get_abs_path()
                src.RemoteUser.pull(path, temp_path) # TODO:需要清除
            else:
                temp_path = os.path.join(config.TMP_PATH, os.path.basename(path))
                src.RemoteUser.pull(path, temp_path)
                cp(target, UFile(local, temp_path))
        elif not isinstance(target.RemoteUser, LocalHost):
            path = src.get_abs_path()
            target.RemoteUser.push(path, target.get_abs_path())

    android = AdbCnet("192.168.121.36")
    linux = Linux("192.168.121.88", "lxb")
    local = LocalHost()
    local.pwd = r"D:\Users\USER\Desktop\flowing\test_data"

    webrtc_path = r"/home/lxb/tool/sourcecode_libs_software_prebuilt_source/webrtc_aec3/src/main/jni/webrtc_core"
    play_path = r"~/warehouse_rv1106/sourcecode/servers/task/voice_play"
    android_lib_path = r"/oem/lib"
    bin_path = r"/home/lxb/warehouse_rv1106/build_tools/output/bin"
    android_bin_path = r"/data/bin"

    # translate .so
    linux.pwd = webrtc_path
    linux.shell("make", "-f", "Makefile.rv1106l")
    webrtc_core = UFile(android, rf"{android_lib_path}/libwebrtc_core.so")
    cp(UFile(android, android_lib_path), webrtc_core)

    linux.pwd = play_path
    linux.shell("./build_cmake.sh")

    @make_style_decorate
    def cp_exe(target:UFile, src:UFile):
        ''' TODO:target may be dir '''
        cp(target, src)
        target.RemoteUser.shell(f"chmod 755 {target.path}")

    linux.pwd = bin_path
    webrtc = UFile(android, f"{android_bin_path}/voice_play")
    cp_exe(webrtc, UFile(linux, "voice_play"))

    pcm_dir = r"/data/pcm"
    rtc_dir = r"D:\Users\USER\Desktop\flowing\test_data\rtc_voice"
    src_to_mix_li = src_to_mix() # 获取一个local src 与 mix 的对应关系
    
    @make_style_decorate
    def webrtc_run(rtced_file:UFile, src_file:UFile, rtc_exe:UFile):
        nonlocal android
        file = UFile(android, "/data/pcm/temp_src.pcm")
        rtc_file = UFile(android, "/data/pcm/temp_rtc.pcm")
        cp(file, src_file, target_count=-1) # target_count=-1 一定执行
        rtc_exe.RemoteUser.shell(rtc_exe.path, file.path, rtc_file.path)
        cp(rtced_file, rtc_file, target_count=-1) 

    local.pwd = r"D:\Users\USER\Desktop\flowing\test_data\rtc_voice"
    similar_data = []
    for src, mixed in src_to_mix_li:
        name = os.path.basename(mixed)
        rtc_name = rf"{name}_rtc.pcm"
        local_rtc_file = UFile(local, rtc_name)
        webrtc_run(local_rtc_file, UFile(local, mixed), webrtc, webrtc_core)
        similar_data.append([src, local_rtc_file]+list(count_mse(src, local_rtc_file.path)))
    
    write_to_csv(similar_data, rf"D:\Users\USER\Desktop\flowing\test_data\result_{time.time()}.csv")
