import subprocess

vid_num = 3

for q in range(vid_num):
    if q > 2:
        cmds = ['C:\\Users\\User\\ffmpeg-4.1-win64-static\\bin\\ffmpeg.exe', '-i', 'M:\Data\GoPro_Visor\Experiment_1\Video\Original\\00' + str(q) + '_01.MP4', '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', 'intermediate1.ts'] 
        subprocess.Popen(cmds) 
        cmds = ['C:\\Users\\User\\ffmpeg-4.1-win64-static\\bin\\ffmpeg.exe', '-i', 'M:\Data\GoPro_Visor\Experiment_1\Video\Original\\00' + str(q) + '_02.MP4', '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', 'intermediate2.ts'] 
        subprocess.Popen(cmds) 
        cmds = ['C:\\Users\\User\\ffmpeg-4.1-win64-static\\bin\\ffmpeg.exe', '-i', '"concat:intermediate1.ts|intermediate2.ts"', '-c', 'copy', '-bsf:a', 'aac_adtstoasc', 'C:\\Users\\User\Desktop\\00' + str(q) + '.avi']
        subprocess.Popen(cmds) 
        print('i')
