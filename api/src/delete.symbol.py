f = open('../final_df (1).csv', 'r')
out = open('../out.csv', 'w')

for line in f:
    out.write(line.replace('"', ''))


f.close()
out.close()
