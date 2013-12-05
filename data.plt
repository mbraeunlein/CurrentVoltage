#set terminal canvas
#set output "data.html"
#set terminal pdf
#set output "data.pdf"
set terminal wxt
set yrange [0:500]
set xrange [0:100000]
plot "data.txt" using 0:1 title 'Voltage' with lines
