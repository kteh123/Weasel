
import pandas

def write(data_frame, file):
    """ Writes a DataFrame as a CSV file"""

    data_frame.to_csv(file)


def read(file):
    """ Reads a DataFrame from a CSV file """  
    
    return pandas.read_csv(file, index_col=0)




               



    



