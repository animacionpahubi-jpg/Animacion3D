# tira.sh NOMBRE → hoja de cuadros (6 por s) de pruebas/ia/NOMBRE.mp4 en el scratchpad
F=$(python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$F" -v error -i pruebas/ia/$1.mp4 -vf "fps=5,scale=230:-1,tile=5x5" -frames:v 1 -y "$2"
