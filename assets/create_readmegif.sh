# asciinema rec assets/readme.cast --overwrite
rm -fr assets/readme.gif
rm -fr assets/readme-cut.gif
rm -fr assets/readme.webp
agg assets/readme.cast assets/readme.gif --speed 1.5 --theme 000000,ffffff,bbbbbb,111111,222222,333333,444444,555555,666666,777777
# gifsicle --color-info assets/readme.gif

gifsicle --colors 256 --background "#000000" -b assets/readme.gif --delete '#0-6' '#103-200'
gif2webp assets/readme.gif -o assets/readme.webp
rm -fr assets/readme.gif
rm -fr assets/readme-cut.gif
xdg-open assets/readme.webp
# xdg-open assets/readme.gif
ls -l assets
